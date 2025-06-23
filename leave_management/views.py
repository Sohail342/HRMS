from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import LeaveBalance, LeaveType
from HRIS_App.models import Employee

# Create your views here.

def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def admin_leave_balance(request):
    """Admin-only view to manage employee leave balances"""
    # Get all leave types for the filter dropdown
    leave_types = LeaveType.objects.filter(is_active=True)
    
    # Get current year and a range of years for the filter dropdown (current year - 2 to current year + 1)
    current_year = timezone.now().year
    years = range(current_year - 2, current_year + 2)
    
    # Initialize queryset with all leave balances
    queryset = LeaveBalance.objects.all().select_related('employee', 'leave_type').order_by('-year', 'employee__name')
    
    # Apply filters based on request parameters
    employee_search = request.GET.get('employee_search')
    leave_type_id = request.GET.get('leave_type')
    year_filter = request.GET.get('year')
    
    if employee_search:
        queryset = queryset.filter(
            Q(employee__name__icontains=employee_search) | 
            Q(employee__SAP_ID__icontains=employee_search)
        )
    
    if leave_type_id:
        queryset = queryset.filter(leave_type_id=leave_type_id)
    
    if year_filter:
        queryset = queryset.filter(year=year_filter)
    
    # Pagination
    paginator = Paginator(queryset, 10)  # Show 10 records per page
    page = request.GET.get('page')
    
    try:
        leave_balances = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        leave_balances = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        leave_balances = paginator.page(paginator.num_pages)
    
    context = {
        'leave_balances': leave_balances,
        'leave_types': leave_types,
        'years': years,
    }
    
    return render(request, 'leave_management/admin_leave_balance.html', context)

def get_leave_balances(request):
    """View to get leave balances for an employee"""
    sap_id = request.GET.get('sap_id')
    print("SAP ID:", sap_id)
    
    if not sap_id:
        return JsonResponse({'error': 'SAP ID is required'}, status=400)
    
    try:
        # Get the employee
        employee = Employee.objects.get(SAP_ID=sap_id)
        
        # Get current year
        current_year = timezone.now().year
        
        # Get leave balances for the employee for the current year
        leave_balances = LeaveBalance.objects.filter(
            employee=employee,
            year=current_year
        )
        
        # Format the balances for the response
        balances_data = []
        for balance in leave_balances:
            balances_data.append({
                'leave_type': balance.leave_type.name,
                'annual_quota': balance.annual_quota,
                'remaining': balance.remaining
            })
        
        return JsonResponse({
            'balances': balances_data
        })
    
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
