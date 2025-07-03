from django.shortcuts import render
from django.shortcuts import render
from django.db.models import Count, Avg, F, Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from HRIS_App.models import Employee, Branch, Region, Division, Wing, Designation

@login_required
def analytics_view(request):
    # Get counts for different entities
    branch_count = Branch.objects.count()
    region_count = Region.objects.count()
    division_count = Division.objects.count()
    wing_count = Wing.objects.count()
    employee_count = Employee.objects.filter(is_active=True).count()
    
    # Get designation counts
    designation_counts = Employee.objects.filter(is_active=True).values('designation__title').annotate(count=Count('id'))
    
    # Get branch operations managers
    bom_employees = Employee.objects.filter(designation__title__icontains='Branch Operations Manager', is_active=True)
    
    # Get regional employees
    re_ops_employees = Employee.objects.filter(designation__title__icontains='RE OPS', is_active=True)
    re_ic_employees = Employee.objects.filter(designation__title__icontains='RE IC', is_active=True)
    
    context = {
        'branch_count': branch_count,
        'region_count': region_count,
        'division_count': division_count,
        'wing_count': wing_count,
        'employee_count': employee_count,
        'designation_counts': designation_counts,
        'bom_employees': bom_employees,
        're_ops_employees': re_ops_employees,
        're_ic_employees': re_ic_employees,
    }
    
    return render(request, 'analytics/analytics.html', context)

@login_required
def bom_report_view(request):
    # Get filter parameters
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    selected_branch = request.GET.get('branch')
    
    # Base queryset for BOM employees
    bom_queryset = Employee.objects.filter(designation__title__icontains='Branch Operations Manager', is_active=True)
    
    # Base queryset for branches
    branches_queryset = Branch.objects.all()
    
    # Apply filters if provided
    if selected_division:
        # Filter employees by division through their region
        # Convert selected_division to integer to avoid type mismatch
        try:
            division_id = int(selected_division)
            regions_in_division = Region.objects.filter(division_id__id=division_id).values_list('id', flat=True)
            bom_queryset = bom_queryset.filter(region_id__in=regions_in_division)
            branches_queryset = branches_queryset.filter(region_id__in=regions_in_division)
        except (ValueError, TypeError):
            # If division_id is not a valid integer, use empty querysets
            bom_queryset = Employee.objects.none()
            branches_queryset = Branch.objects.none()
    
    if selected_region:
        try:
            # Convert selected_region to integer to avoid type mismatch
            region_id = int(selected_region)
            region = Region.objects.get(id=region_id)
            bom_queryset = bom_queryset.filter(region__name=region.name)
            branches_queryset = branches_queryset.filter(region__name=region.name)
        except (ValueError, TypeError, Region.DoesNotExist):
            # If region_id is not a valid integer or region doesn't exist, use empty querysets
            bom_queryset = Employee.objects.none()
            branches_queryset = Branch.objects.none()
    
    if selected_branch:
        try:
            # Convert selected_branch to integer to avoid type mismatch
            branch_id = int(selected_branch)
            branch = Branch.objects.get(id=branch_id)
            bom_queryset = bom_queryset.filter(branch__branch_name=branch.branch_name)
            branches_queryset = branches_queryset.filter(id=branch_id)
        except (ValueError, TypeError, Branch.DoesNotExist):
            # If branch_id is not a valid integer or branch doesn't exist, use empty querysets
            bom_queryset = Employee.objects.none()
            branches_queryset = Branch.objects.none()
    
    # Get all divisions, regions, and branches for filter dropdowns
    divisions = Division.objects.all()
    regions = Region.objects.all()
    branches = Branch.objects.all()
    
    # Calculate KPI metrics
    total_bom = bom_queryset.count()
    
    branches_with_bom_ids = [int(b.branch.id) if b.branch and b.branch.id else 0 for b in bom_queryset]
    branches_with_bom_count = branches_queryset.filter(id__in=branches_with_bom_ids).count()
    
    # Get branches without BOM
    branches_without_bom_count = branches_queryset.exclude(id__in=branches_with_bom_ids).count()
    
    # Get branches where BM is acting as BOM
    branches_without_bom = branches_queryset.exclude(id__in=branches_with_bom_ids)
    bm_as_bom_count = Employee.objects.filter(
        designation__title__icontains='Branch Manager',
        branch__in=branches_without_bom
    ).count()
    
    # Current year for upgrade/downgrade calculations
    current_year = timezone.now().year
    start_of_year = datetime(current_year, 1, 1)
    
    # Staff upgraded to BOM in current year
    # This is a simplified approach - in a real system, you'd track grade changes
    # Since date_of_joining is a CharField, we need to filter differently
    current_year_str = str(current_year)
    upgraded_to_bom = bom_queryset.filter(
        date_of_joining__contains=current_year_str
    ).count()
    
    # Staff downgraded from BOM in current year
    # This is a simplified approach - in a real system, you'd track grade changes
    downgraded_from_bom = 0  # Placeholder - would need historical data
    
    # Calculate average years as BOM
    # This is a simplified approach - in a real system, you'd track tenure in role
    current_date = timezone.now().date()
    
    # Since date_of_joining is a CharField, we can't do date arithmetic directly
    # Setting a default value instead
    avg_years_as_bom = 0
    
    # In a real implementation, you would need to parse the date strings
    # and calculate the average tenure
    
    # Age distribution
    age_distribution = {
        '20-30': 0,
        '31-40': 0,
        '41-50': 0,
        '51+': 0
    }
    
    
    # Placeholder values for demonstration
    age_distribution['20-30'] = 0
    age_distribution['31-40'] = 0
    age_distribution['41-50'] = 0
    age_distribution['51+'] = 0
    
    # Gender distribution
    # Since there's no gender field in the Employee model, we'll use a placeholder
    gender_dist = {
        'Not Specified': bom_queryset.count()
    }
    
    # Prepare detailed branch data
    branch_bom_data = []
    
    for branch in branches_queryset:
        # Check if branch has a BOM
        branch_bom = bom_queryset.filter(branch=branch).first()
        
        # Check if BM is acting as BOM
        bm_acting_as_bom = False
        assigned_person = None
        role = None
        age = None
        gender = None
        years_as_bom = None
        status = None
        
        if branch_bom:
            # Branch has a dedicated BOM
            assigned_person = branch_bom.name
            role = 'BOM'
            # Since birth_date is a CharField, we can't do date arithmetic
            # In a real implementation, you would need to parse the date string
            age = None  # Setting to None as we can't calculate it
            gender = 'Not Specified'  # Since there's no gender field in the Employee model
            # Since date_of_joining is a CharField, we can't do date arithmetic
            # In a real implementation, you would need to parse the date string
            years_as_bom = 0  # Setting a default value
            
            # Determine upgrade/downgrade status (simplified)
            # Since date_of_joining is a CharField, we need to check differently
            if branch_bom.date_of_joining and current_year_str in branch_bom.date_of_joining:
                status = 'Upgraded'
        else:
            # Check if BM is acting as BOM
            branch_bm = Employee.objects.filter(
                branch=branch,
                designation__title__icontains='Branch Manager',
                is_active=True
            ).first()
            
            if branch_bm:
                bm_acting_as_bom = True
                assigned_person = branch_bm.name
                role = 'BM acting as BOM'
                # Since birth_date is a CharField, we can't do date arithmetic
                # In a real implementation, you would need to parse the date string
                age = None  # Setting to None as we can't calculate it
                gender = 'Not Specified'  # Since there's no gender field in the Employee model
                years_as_bom = 0  # Not officially a BOM
        
        # Get division name through region if available
        division_name = 'N/A'
        if branch.region and hasattr(branch.region, 'division_id') and branch.region.division_id:
            try:
                # Access the division directly through the ForeignKey
                division_name = branch.region.division_id.division_name
            except Exception:
                pass
        
        branch_data = {
            'branch_code': branch.branch_code,
            'branch_name': branch.branch_name,
            'division': division_name,
            'region': branch.region.name if branch.region else 'N/A',
            'bom_assigned': bool(branch_bom),
            'bm_acting_as_bom': bm_acting_as_bom,
            'assigned_person': assigned_person,
            'role': role,
            'age': age,
            'gender': gender,
            'years_as_bom': years_as_bom,
            'status': status
        }
        
        branch_bom_data.append(branch_data)
    
    context = {
        'total_bom': total_bom,
        'branches_with_bom': branches_with_bom_count,
        'branches_without_bom': branches_without_bom_count,
        'bm_as_bom': bm_as_bom_count,
        'upgraded_to_bom': upgraded_to_bom,
        'downgraded_from_bom': downgraded_from_bom,
        'avg_years_as_bom': avg_years_as_bom,
        'age_distribution': age_distribution,
        'gender_distribution': gender_dist,
        'branch_bom_data': branch_bom_data,
        'divisions': divisions,
        'regions': regions,
        'branches': branches,
        'selected_division': selected_division,
        'selected_region': selected_region,
        'selected_branch': selected_branch,
    }
    
    return render(request, 'analytics/bom_report.html', context)

@login_required
def api_regions(request):
    """API endpoint to get regions filtered by division"""
    division_id = request.GET.get('division')
    
    regions = Region.objects.all()
    if division_id:
        # Use division_id__id to access the ID of the ForeignKey
        regions = regions.filter(division_id__id=division_id)
    
    regions_data = [{'id': region.id, 'name': region.name} for region in regions]
    return JsonResponse(regions_data, safe=False)

@login_required
def api_branches(request):
    """API endpoint to get branches filtered by region"""
    region_id = request.GET.get('region')
    
    branches = Branch.objects.all()
    if region_id:
        # Get the region name from the region ID
        try:
            region = Region.objects.get(id=region_id)
            branches = branches.filter(region__name=region.name)
        except Region.DoesNotExist:
            # If region doesn't exist, return empty list
            branches = Branch.objects.none()
    
    branches_data = [{'id': branch.id, 'branch_name': branch.branch_name} for branch in branches]
    return JsonResponse(branches_data, safe=False)