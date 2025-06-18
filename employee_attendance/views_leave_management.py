from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse
from datetime import date, datetime, timedelta
from group_head.decorators import employee_user_required
from HRIS_App.models import Employee, EmployeeType

from .models_leave_management import (
    LeaveType,
    EmployeeLeavePolicy,
    LeavePeriod,
    EmployeeLeaveBalance,
    EmployeeLeaveApplication,
    LeaveTransaction
)

from .forms_leave_management import (
    LeaveApplicationForm,
    LeaveBalanceAdjustmentForm,
    LeaveTypeForm,
    EmployeeLeavePolicyForm,
    LeavePeriodForm
)


@login_required
def leave_management_dashboard(request):
    """Dashboard view for leave management"""
    # Get employee type for the current user
    employee = request.user
    
    # Summary statistics
    total_employees = Employee.objects.exclude(is_admin=True).count()
    total_leave_requests = EmployeeLeaveApplication.objects.count()
    pending_approvals = EmployeeLeaveApplication.objects.filter(leave_status="pending").count()
    
    # Get leave balances for the current user
    current_year = date.today().year
    leave_balances = EmployeeLeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    )
    
    # Get recent leave applications for the current user
    recent_applications = EmployeeLeaveApplication.objects.filter(
        employee=employee
    ).order_by('-application_date')[:5]
    
    # For admin users, show pending leave applications
    pending_leave_requests = []
    if employee.is_admin or employee.is_letter_template_admin:
        pending_leave_requests = EmployeeLeaveApplication.objects.filter(
            leave_status="pending"
        ).order_by('application_date')[:10]
    
    context = {
        'total_employees': total_employees,
        'total_leave_requests': total_leave_requests,
        'pending_approvals': pending_approvals,
        'leave_balances': leave_balances,
        'recent_applications': recent_applications,
        'pending_leave_requests': pending_leave_requests,
    }
    
    return render(request, "employee_attendance/leave_management_dashboard.html", context)


@login_required
@employee_user_required
def apply_leave(request):
    """View for employees to apply for leave"""
    employee = request.user
    
    # Get employee type and applicable leave types
    employee_type = employee.employee_type
    
    # Get leave policies for this employee type
    leave_policies = EmployeeLeavePolicy.objects.filter(
        employee_type=employee_type,
        is_active=True
    )
    
    # Get leave types available for this employee type
    available_leave_types = LeaveType.objects.filter(
        id__in=leave_policies.values_list('leave_type_id', flat=True),
        is_active=True
    )
    
    # Get current leave balances
    current_year = date.today().year
    leave_balances = EmployeeLeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    )
    
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST, employee=employee)
        if form.is_valid():
            leave_application = form.save(commit=False)
            leave_application.employee = employee
            leave_application.application_date = date.today()
            leave_application.save()
            
            messages.success(request, "Leave application submitted successfully.")
            return redirect('employee_attendance:leave_management_dashboard')
    else:
        form = LeaveApplicationForm()
        # Limit leave type choices to available types
        form.fields['leave_type'].queryset = available_leave_types
    
    context = {
        'form': form,
        'leave_balances': leave_balances,
        'employee': employee,
    }
    
    return render(request, 'employee_attendance/apply_leave.html', context)


@login_required
def view_leave_history(request):
    """View for employees to see their leave history"""
    employee = request.user
    
    # Get all leave applications for this employee
    leave_applications = EmployeeLeaveApplication.objects.filter(
        employee=employee
    ).order_by('-application_date')
    
    # Get leave transactions for this employee
    leave_transactions = LeaveTransaction.objects.filter(
        employee=employee
    ).order_by('-transaction_date')
    
    context = {
        'leave_applications': leave_applications,
        'leave_transactions': leave_transactions,
    }
    
    return render(request, 'employee_attendance/leave_history.html', context)


@login_required
def view_leave_balances(request):
    """View for employees to see their leave balances"""
    employee = request.user
    current_year = date.today().year
    
    # Get leave balances for the current year
    leave_balances = EmployeeLeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    )
    
    # Get leave policies for this employee type
    employee_type = employee.employee_type
    leave_policies = EmployeeLeavePolicy.objects.filter(
        employee_type=employee_type,
        is_active=True
    )
    
    context = {
        'leave_balances': leave_balances,
        'leave_policies': leave_policies,
        'current_year': current_year,
    }
    
    return render(request, 'employee_attendance/leave_balances.html', context)


@login_required
def approve_leave(request, application_id):
    """View for approving leave applications"""
    if not (request.user.is_admin or request.user.is_letter_template_admin):
        messages.error(request, "You don't have permission to approve leave applications.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    leave_application = get_object_or_404(EmployeeLeaveApplication, id=application_id)
    
    if leave_application.leave_status != 'pending':
        messages.error(request, "This leave application has already been processed.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    # Process the leave application
    with transaction.atomic():
        # Update leave application status
        leave_application.leave_status = 'approved'
        leave_application.save()
        
        # Update leave balance
        employee = leave_application.employee
        leave_type = leave_application.leave_type
        current_year = date.today().year
        
        try:
            balance = EmployeeLeaveBalance.objects.get(
                employee=employee,
                leave_type=leave_type,
                year=current_year
            )
            
            # Update used leaves
            balance.used_leaves += leave_application.availed_leaves
            balance.save()
            
        except EmployeeLeaveBalance.DoesNotExist:
            # If no balance record exists, create one based on policy
            try:
                policy = EmployeeLeavePolicy.objects.get(
                    employee_type=employee.employee_type,
                    leave_type=leave_type,
                    is_active=True
                )
                
                # Create a new balance record
                balance = EmployeeLeaveBalance.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    year=current_year,
                    entitled_leaves=policy.annual_entitlement,
                    used_leaves=leave_application.availed_leaves
                )
                
            except EmployeeLeavePolicy.DoesNotExist:
                messages.error(request, "No leave policy found for this employee type and leave type.")
                return redirect('employee_attendance:leave_management_dashboard')
        
        # Create a leave transaction record
        LeaveTransaction.objects.create(
            employee=employee,
            leave_type=leave_type,
            leave_application=leave_application,
            transaction_type='usage',
            transaction_date=date.today(),
            days=-leave_application.availed_leaves,  # Negative for deduction
            year=current_year,
            notes=f"Leave approved from {leave_application.from_date} to {leave_application.to_date}"
        )
    
    messages.success(request, f"Leave application for {employee.name} approved successfully.")
    return redirect('employee_attendance:leave_management_dashboard')


@login_required
def decline_leave(request, application_id):
    """View for declining leave applications"""
    if not (request.user.is_admin or request.user.is_letter_template_admin):
        messages.error(request, "You don't have permission to decline leave applications.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    leave_application = get_object_or_404(EmployeeLeaveApplication, id=application_id)
    
    if leave_application.leave_status != 'pending':
        messages.error(request, "This leave application has already been processed.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    # Update leave application status
    leave_application.leave_status = 'declined'
    leave_application.save()
    
    messages.success(request, f"Leave application for {leave_application.employee.name} declined.")
    return redirect('employee_attendance:leave_management_dashboard')


@login_required
def adjust_leave_balance(request):
    """View for manual adjustment of leave balances (admin only)"""
    if not (request.user.is_admin or request.user.is_letter_template_admin):
        messages.error(request, "You don't have permission to adjust leave balances.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    if request.method == 'POST':
        form = LeaveBalanceAdjustmentForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            leave_type = form.cleaned_data['leave_type']
            adjustment_type = form.cleaned_data['adjustment_type']
            days = form.cleaned_data['days']
            reason = form.cleaned_data['reason']
            current_year = date.today().year
            
            with transaction.atomic():
                # Get or create leave balance record
                balance, created = EmployeeLeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type=leave_type,
                    year=current_year,
                    defaults={
                        'entitled_leaves': 0,
                        'carried_forward_leaves': 0,
                        'used_leaves': 0,
                        'frozen_leaves': 0
                    }
                )
                
                # Process adjustment based on type
                transaction_type = ''
                transaction_days = 0
                
                if adjustment_type == 'add':
                    balance.entitled_leaves += days
                    transaction_type = 'adjustment'
                    transaction_days = days
                
                elif adjustment_type == 'deduct':
                    balance.used_leaves += days
                    transaction_type = 'adjustment'
                    transaction_days = -days
                
                elif adjustment_type == 'freeze':
                    balance.entitled_leaves -= days
                    balance.frozen_leaves += days
                    transaction_type = 'freeze'
                    transaction_days = days
                
                elif adjustment_type == 'unfreeze':
                    balance.frozen_leaves -= days
                    balance.entitled_leaves += days
                    transaction_type = 'adjustment'
                    transaction_days = days
                
                # Save balance
                balance.save()
                
                # Create transaction record
                LeaveTransaction.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    transaction_type=transaction_type,
                    transaction_date=date.today(),
                    days=transaction_days,
                    year=current_year,
                    notes=reason
                )
            
            messages.success(request, f"Leave balance for {employee.name} adjusted successfully.")
            return redirect('employee_attendance:leave_management_dashboard')
    else:
        form = LeaveBalanceAdjustmentForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'employee_attendance/adjust_leave_balance.html', context)


@login_required
def process_year_end(request):
    """View for processing year-end leave operations (admin only)"""
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to process year-end operations.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    if request.method == 'POST':
        current_year = date.today().year
        next_year = current_year + 1
        
        # Process all employee types
        employee_types = EmployeeType.objects.all()
        
        with transaction.atomic():
            for employee_type in employee_types:
                # Get leave policies for this employee type
                leave_policies = EmployeeLeavePolicy.objects.filter(
                    employee_type=employee_type,
                    is_active=True
                )
                
                # Get employees of this type
                employees = Employee.objects.filter(employee_type=employee_type, is_active=True)
                
                for employee in employees:
                    for policy in leave_policies:
                        leave_type = policy.leave_type
                        
                        # Get current year balance
                        try:
                            current_balance = EmployeeLeaveBalance.objects.get(
                                employee=employee,
                                leave_type=leave_type,
                                year=current_year
                            )
                            
                            # Calculate leaves to carry forward
                            available_leaves = current_balance.available_leaves
                            carry_forward_leaves = min(available_leaves, policy.carry_forward_limit)
                            
                            # Calculate expiry date for carried forward leaves
                            carry_forward_expiry_date = None
                            if carry_forward_leaves > 0 and policy.carry_forward_expiry_months > 0:
                                carry_forward_expiry_date = date(next_year, 3, 31)  # March 31 of next year
                            
                            # Create next year's balance
                            next_year_balance, created = EmployeeLeaveBalance.objects.get_or_create(
                                employee=employee,
                                leave_type=leave_type,
                                year=next_year,
                                defaults={
                                    'entitled_leaves': policy.annual_entitlement,
                                    'carried_forward_leaves': carry_forward_leaves,
                                    'carried_forward_expiry_date': carry_forward_expiry_date,
                                    'used_leaves': 0,
                                    'frozen_leaves': current_balance.frozen_leaves  # Transfer frozen leaves
                                }
                            )
                            
                            # If balance already exists, update it
                            if not created:
                                next_year_balance.entitled_leaves = policy.annual_entitlement
                                next_year_balance.carried_forward_leaves = carry_forward_leaves
                                next_year_balance.carried_forward_expiry_date = carry_forward_expiry_date
                                next_year_balance.frozen_leaves = current_balance.frozen_leaves
                                next_year_balance.save()
                            
                            # Create transaction records
                            if carry_forward_leaves > 0:
                                LeaveTransaction.objects.create(
                                    employee=employee,
                                    leave_type=leave_type,
                                    transaction_type='carry_forward',
                                    transaction_date=date.today(),
                                    days=carry_forward_leaves,
                                    year=next_year,
                                    notes=f"Carried forward from {current_year}"
                                )
                            
                            # Handle expired leaves
                            expired_leaves = available_leaves - carry_forward_leaves
                            if expired_leaves > 0:
                                LeaveTransaction.objects.create(
                                    employee=employee,
                                    leave_type=leave_type,
                                    transaction_type='expire',
                                    transaction_date=date.today(),
                                    days=-expired_leaves,  # Negative for deduction
                                    year=current_year,
                                    notes=f"Expired at year-end {current_year}"
                                )
                            
                        except EmployeeLeaveBalance.DoesNotExist:
                            # If no current balance, create a new one for next year with default entitlement
                            EmployeeLeaveBalance.objects.create(
                                employee=employee,
                                leave_type=leave_type,
                                year=next_year,
                                entitled_leaves=policy.annual_entitlement,
                                carried_forward_leaves=0,
                                used_leaves=0,
                                frozen_leaves=0
                            )
        
        messages.success(request, f"Year-end processing completed successfully for {current_year}.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    return render(request, 'employee_attendance/process_year_end.html')


@login_required
def leave_policy_management(request):
    """View for managing leave policies (admin only)"""
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to manage leave policies.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    # Get all leave types, policies, and periods
    leave_types = LeaveType.objects.all()
    leave_policies = EmployeeLeavePolicy.objects.all()
    leave_periods = LeavePeriod.objects.all()
    
    context = {
        'leave_types': leave_types,
        'leave_policies': leave_policies,
        'leave_periods': leave_periods,
    }
    
    return render(request, 'employee_attendance/leave_policy_management.html', context)


@login_required
def add_leave_type(request):
    """View for adding or editing leave types (admin only)"""
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to manage leave types.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    # Check if we're editing an existing leave type
    leave_type_id = request.POST.get('leave_type_id')
    edit_leave_type = None
    
    if leave_type_id:
        edit_leave_type = get_object_or_404(LeaveType, id=leave_type_id)
    
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=edit_leave_type)
        if form.is_valid():
            form.save()
            if edit_leave_type:
                messages.success(request, "Leave type updated successfully.")
            else:
                messages.success(request, "Leave type added successfully.")
            return redirect('employee_attendance:leave_policy_management')
    else:
        form = LeaveTypeForm(instance=edit_leave_type)
    
    context = {
        'form': form,
        'edit_leave_type': edit_leave_type,
    }
    
    return render(request, 'employee_attendance/leave_policy_management.html', context)


@login_required
def add_leave_policy(request):
    """View for adding or editing leave policies (admin only)"""
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to manage leave policies.")
        return redirect('employee_attendance:leave_management_dashboard')
    
    # Check if we're editing an existing policy
    policy_id = request.POST.get('policy_id')
    edit_policy = None
    
    if policy_id:
        edit_policy = get_object_or_404(EmployeeLeavePolicy, id=policy_id)
    
    if request.method == 'POST':
        form = EmployeeLeavePolicyForm(request.POST, instance=edit_policy)
        if form.is_valid():
            form.save()
            if edit_policy:
                messages.success(request, "Leave policy updated successfully.")
            else:
                messages.success(request, "Leave policy added successfully.")
            return redirect('employee_attendance:leave_policy_management')
    else:
        form = EmployeeLeavePolicyForm(instance=edit_policy)
    
    # Get all leave types for the form
    leave_types = LeaveType.objects.all()
    
    context = {
        'form': form,
        'edit_policy': edit_policy,
        'leave_types': leave_types,
    }
    
    return render(request, 'employee_attendance/leave_policy_management.html', context)
