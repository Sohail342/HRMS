from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from HRIS_App.models import Employee

from .models import (
    LeaveType, LeaveRule, LeaveBalance, EmployeeProfile,
    FrozenLeaveBalance, LeaveManagement
)


def assign_all_employee_leave_balances():
    """
    Assign leave balances to all employees based on their profiles and leave rules.
    """
    current_year = datetime.now().year
    profiles = EmployeeProfile.objects.select_related("employee")

    for profile in profiles:
        rules = LeaveRule.objects.filter(
            cadre=profile.cadre,
            employment_type=profile.employment_type
        )

        for rule in rules:
            LeaveBalance.objects.update_or_create(
                employee=profile.employee,
                leave_type=rule.leave_type,
                year=current_year,
                defaults={
                    "annual_quota": rule.annual_quota,
                    "remaining": rule.annual_quota,
                }
            )


def create_employee_profiles_from_employees():
    """
    Create EmployeeProfile for all Employees who don't have one.
    Cadre and employment_type are taken from related Employee fields.
    """
    created_count = 0
    skipped = 0

    for emp in Employee.objects.select_related('cadre', 'employee_type'):
        if hasattr(emp, 'employeeprofile'):
            skipped += 1
            continue

        # Safely get cadre and employment_type as string
        cadre = emp.cadre.name if emp.cadre else None
        employment_type = emp.employee_type.name if emp.employee_type else None

        if not cadre or not employment_type:
            skipped += 1
            continue  # Skip if required info missing

        # Create EmployeeProfile
        EmployeeProfile.objects.create(
            employee=emp,
            cadre=cadre,
            employment_type=employment_type
        )
        created_count += 1

    return f"✅ Created: {created_count} profiles | Skipped: {skipped}"



def initialize_leave_balances_for_new_year(year=None):
    """
    Create leave balances for all employees for a new year.
    """
    year = year or datetime.now().year
    profiles = EmployeeProfile.objects.select_related("employee")

    created_count = 0
    for profile in profiles:
        rules = LeaveRule.objects.filter(
            cadre=profile.cadre,
            employment_type=profile.employment_type
        )

        for rule in rules:
            leave_balance, created = LeaveBalance.objects.get_or_create(
                employee=profile.employee,
                leave_type=rule.leave_type,
                year=year,
                defaults={
                    "annual_quota": rule.annual_quota,
                    "remaining": rule.annual_quota
                }
            )
            if created:
                created_count += 1

    return f"✅ Initialized leave balances for year {year}. New entries: {created_count}"




def get_leave_cycle(employee_profile: EmployeeProfile):
    today = date.today()
    if employee_profile.employment_type == "Contractual" and employee_profile.contract_start_date:
        start = employee_profile.contract_start_date
        end = start + relativedelta(years=1)
    elif employee_profile.cadre == "Executive":
        start = date(today.year, 1, 1)
        end = date(today.year + 1, 3, 31)
    else:
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
    return (start, end)


def validate_leave_application(employee, leave_type, start_date, end_date, is_mandatory=False):
    """
    Validate leave application based on rules for current year:  
    - Leave dates must fall within the employee's leave cycle
    - Sufficient leave balance for the requested type
    - If mandatory leave, check mandatory balance
    """
    profile = employee.employeeprofile
    cycle_start, cycle_end = get_leave_cycle(profile)
    if start_date < cycle_start or end_date > cycle_end + timedelta(days=30):
        raise ValidationError("Leave dates must fall within your leave cycle.")

    try:
        leave_balance = LeaveBalance.objects.get(employee=employee, leave_type=leave_type, year=datetime.now().year)
    except LeaveBalance.DoesNotExist:
        raise ValidationError("Leave balance not set for this type.")
    except LeaveBalance.MultipleObjectsReturned:
        # Handle the case where multiple leave balances exist
        leave_balance = LeaveBalance.objects.filter(employee=employee, leave_type=leave_type).last()
        
        if not leave_balance:
            raise ValidationError("Leave balance not set for this type.")
        
    # Check if employee has zero balance
    if leave_balance.remaining == 0:
        raise ValidationError(f"You have 0 {leave_type.name} leaves remaining. Cannot apply for this leave type.")

    requested_days = (end_date - start_date).days + 1
    
    # Handle mandatory leave validation for Privileged leave
    if is_mandatory and leave_type.name == 'Privileged':
        # Check if mandatory leave balance exists, if not, initialize it
        if leave_balance.mandatory_annual_quota == 0:
            raise ValidationError("Mandatory leave balance reach out.")
          
        leave_balance.mandatory_remaining = min(15, leave_balance.mandatory_remaining)
        leave_balance.save()
        
        # Check if mandatory leave balance is sufficient
        if leave_balance.mandatory_remaining < requested_days:
            raise ValidationError(f"Insufficient mandatory leave balance. You have {leave_balance.mandatory_remaining} mandatory days remaining.")
    else:
        # Regular leave balance check
        if leave_balance.remaining < requested_days:
            raise ValidationError("Insufficient leave balance.")


def apply_for_leave(employee, leave_type, start_date, end_date, reason, is_mandatory=False):
    # 1. Validate application rules (cycle range, sufficient balance, etc.)
    validate_leave_application(employee, leave_type, start_date, end_date, is_mandatory)

    # 2. Calculate number of leave days
    leave_days = (end_date - start_date).days + 1

    # 3. Create the leave record (status = Pending)
    leave = LeaveManagement.objects.create(
        employee=employee,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status='Pending',
        is_mandatory=is_mandatory if leave_type.name == 'Privileged' else False
    )

    return {
        "success": True,
        "message": f"{leave_days} day(s) leave application submitted and is pending approval.",
        "leave_id": leave.id,
    }


def freeze_and_carry_forward_leaves(year):
    balances = LeaveBalance.objects.filter(year=year)
    for lb in balances:
        leave_type = lb.leave_type

        if leave_type.is_freezable and lb.remaining > 0:
            FrozenLeaveBalance.objects.create(
                employee=lb.employee,
                leave_type=leave_type,
                year=year,
                days=lb.remaining
            )
            print(f"Froze {lb.remaining} days of {leave_type.name} for {lb.employee.name}")
        
        lb.remaining = 0
        lb.save()


def expire_privileged_leaves():
    privileged = LeaveType.objects.get(name="Privileged")
    today = date.today()
    if today > date(today.year, 3, 31):
        for profile in EmployeeProfile.objects.filter(employment_type="Regular"):
            LeaveBalance.objects.filter(
                employee=profile.employee,
                leave_type=privileged
            ).update(remaining=0)


def is_eligible_for_encashment(employee):
    profile = employee.employeeprofile
    if profile.cadre != "Officer" or profile.employment_type != "Regular":
        return False

    privileged = LeaveType.objects.get(name="Privileged")
    leaves = LeaveManagement.objects.filter(
        employee=employee,
        leave_type=privileged,
        status="Approved",
        start_date__year=datetime.now().year, 
        is_mandatory=True
    )

    total_days = sum([(leave.end_date - leave.start_date).days + 1 for leave in leaves])
    return total_days >= 15
