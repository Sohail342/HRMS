from django.shortcuts import render
from django.db.models import Count, Avg, F, Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from HRIS_App.models import Employee, Branch, Region, Division, Wing, Designation, Cadre, EmployeeType, EmployeeGrade, Qualification, APA_Grading
from django.core.paginator import Paginator

def calculate_gender_distribution(employees_queryset):
    """Calculate gender distribution based on CNIC number
    
    Args:
        employees_queryset: QuerySet of Employee objects
        
    Returns:
        Dictionary with gender distribution counts
    """
    male_count = 0
    female_count = 0
    other_count = 0
    
    for employee in employees_queryset:
        if employee.cnic_no and len(employee.cnic_no) > 0:
            # Get the last digit of CNIC
            last_digit = int(employee.cnic_no[-1])
            # Even last digit means female, odd means male
            if last_digit % 2 == 0:
                female_count += 1
            else:
                male_count += 1
        else:
            other_count += 1
            
    return {
        'Male': male_count,
        'Female': female_count,
        'Other': other_count,
    }

@login_required
def analytics_view(request):
    """Main analytics dashboard view"""
    context = {
        'branch_count': Branch.objects.count(),
        'region_count': Region.objects.count(),
        'division_count': Division.objects.count(),
        'wing_count': Wing.objects.count(),
        'employee_count': Employee.objects.filter(is_active=True).count(),
        'designation_counts': Employee.objects.filter(is_active=True)
                                .values('designation__title')
                                .annotate(count=Count('SAP_ID')),
        'bom_employees': Employee.objects.filter(
                            designation__title__icontains='Branch Operations Manager', 
                            is_active=True
                        ),
        're_ops_employees': Employee.objects.filter(
                               designation__title__icontains='RE OPS', 
                               is_active=True
                           ),
        're_ic_employees': Employee.objects.filter(
                              designation__title__icontains='RE IC', 
                              is_active=True
                          ),
    }
    return render(request, 'analytics/analytics.html', context)

@login_required
def bom_report_view(request):
    """Branch Operations Manager report view"""
    # Get filter parameters
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    selected_branch = request.GET.get('branch')
    
    # Initialize base querysets with select_related for performance
    bom_queryset = Employee.objects.filter(
        designation__title__icontains='Branch Operations Manager',
        is_active=True
    ).select_related('branch', 'region', 'designation')
    
    branches_queryset = Branch.objects.all().select_related('region')

    # Apply filters if provided
    if selected_division:
        try:
            division_name = int(selected_division)
            regions_in_division = Region.objects.filter(
                division_id=division_name
            ).values_list('id', flat=True)
            
            # Convert to list of integers to ensure type consistency
            region_ids = [int(rid) for rid in regions_in_division]
            bom_queryset = bom_queryset.filter(region_id__in=region_ids)
            branches_queryset = branches_queryset.filter(region_id__in=region_ids)
        except (ValueError, TypeError):
            bom_queryset = Employee.objects.none()
            branches_queryset = Branch.objects.none()

    if selected_region:
        try:
            region_id = int(selected_region)
            bom_queryset = bom_queryset.filter(region_id=region_id)
            branches_queryset = branches_queryset.filter(region_id=region_id)
        except (ValueError, TypeError):
            bom_queryset = Employee.objects.none()
            branches_queryset = Branch.objects.none()

    if selected_branch:
        try:
            branch_id = int(selected_branch)
            bom_queryset = bom_queryset.filter(branch_id=branch_id)
            branches_queryset = branches_queryset.filter(id=branch_id)
        except (ValueError, TypeError):
            bom_queryset = Employee.objects.none()
            branches_queryset = Branch.objects.none()

    # Get filter options - using values() for better performance
    divisions = Division.objects.all().values('id', 'division_name').order_by('division_name')
    regions = Region.objects.all().values('id', 'name').order_by('name')
    branches = Branch.objects.all().values('id', 'branch_name').order_by('branch_name')

    # Calculate KPI metrics
    total_bom = bom_queryset.count()
    
    # Get branches with BOM - ensure we're working with branch names (strings)
    branch_names_with_bom = list(bom_queryset.values_list('branch__branch_name', flat=True).distinct())
    branches_with_bom = branches_queryset.filter(branch_name__in=branch_names_with_bom)
    branches_with_bom_count = branches_with_bom.count()
    
    # Get branches without BOM
    branches_without_bom = branches_queryset.exclude(
        branch_name__in=branch_names_with_bom
    )
    branches_without_bom_count = branches_without_bom.count()
    
    # Branches where BM is acting as BOM
    bm_as_bom_count = Employee.objects.filter(
        designation__title__icontains='Branch Manager',
        branch__branch_name__in=branches_without_bom.values_list('branch_name', flat=True),
        is_active=True
    ).count()
    
    # Current year calculations
    current_year = timezone.now().year
    current_year_str = str(current_year)
    
    # Staff upgraded to BOM in current year
    upgraded_to_bom = bom_queryset.filter(
        date_of_joining__contains=current_year_str
    ).count()
    
    # Prepare detailed branch data
    branch_bom_data = []
    for branch in branches_queryset:
        branch_bom = bom_queryset.filter(branch__branch_name=branch.branch_name).first()
        
        # Get BM acting as BOM if no dedicated BOM
        branch_bm = None
        if not branch_bom:
                branch_bm = Employee.objects.filter(
                branch__branch_name=branch.branch_name,
                designation__title__icontains='Branch Manager',
                is_active=True
            ).first()
        
        # Get division name through region
        division_name = 'N/A'
        if branch.region and branch.region.division_id:
            division_name = branch.region.division_id.division_name
        
        branch_data = {
            'branch_code': branch.branch_code,
            'branch_name': branch.branch_name,
            'division': division_name,
            'region': branch.region.name if branch.region else 'N/A',
            'bom_assigned': bool(branch_bom),
            'bm_acting_as_bom': bool(not branch_bom and branch_bm),
            'assigned_person': branch_bom.name if branch_bom else (branch_bm.name if branch_bm else None),
            'role': 'BOM' if branch_bom else ('BM acting as BOM' if branch_bm else None),
            'status': 'Upgraded' if branch_bom and branch_bom.date_of_joining and current_year_str in branch_bom.date_of_joining else None
        }
        branch_bom_data.append(branch_data)
    
    context = {
        'total_bom': total_bom,
        'branches_with_bom': branches_with_bom_count,
        'branches_without_bom': branches_without_bom_count,
        'bm_as_bom': bm_as_bom_count,
        'upgraded_to_bom': upgraded_to_bom,
        'downgraded_from_bom': 0,  # Placeholder
        'avg_years_as_bom': 0,     # Placeholder
        'age_distribution': {
            '20-30': total_bom // 4,
            '31-40': total_bom // 4,
            '41-50': total_bom // 4,
            '51+': total_bom - 3*(total_bom // 4)
        },
        'gender_distribution': calculate_gender_distribution(bom_queryset),
        'branch_bom_data': branch_bom_data,
        'divisions': list(divisions),
        'regions': list(regions),
        'branches': list(branches),
        'selected_division': selected_division,
        'selected_region': selected_region,
        'selected_branch': selected_branch,
    }
    return render(request, 'analytics/bom_report.html', context)

@login_required
def api_regions(request):
    """API endpoint to get regions filtered by division"""
    division_name = request.GET.get('division')
    
    regions = Region.objects.all()
    if division_name:
        try:
            division = Division.objects.get(id=division_name)
            regions = regions.filter(division_id=division)
        except (ValueError, TypeError, Division.DoesNotExist):
            return JsonResponse([], safe=False)
    
    regions_data = [{'id': region.id, 'name': region.name} for region in regions]
    return JsonResponse(regions_data, safe=False)

@login_required
def api_branches(request):
    """API endpoint to get branches filtered by region"""
    region_id = request.GET.get('region')
    
    branches = Branch.objects.all()
    if region_id:
        try:
            region = Region.objects.get(id=region_id)
            branches = branches.filter(region=region)
        except (ValueError, TypeError, Region.DoesNotExist):
            return JsonResponse([], safe=False)
    
    branches_data = [{'id': branch.id, 'branch_name': branch.branch_name} for branch in branches]
    return JsonResponse(branches_data, safe=False)

@login_required
def api_wings(request):
    """API endpoint to get wings filtered by division"""
    division_name = request.GET.get('division')
    
    wings = Wing.objects.all()
    if division_name:
        try:
            division = Division.objects.get(id=division_name)
            wings = wings.filter(division_id=division)
        except (ValueError, TypeError, Division.DoesNotExist):
            return JsonResponse([], safe=False)
    
    wings_data = [{'id': wing.id, 'name': wing.name} for wing in wings]
    return JsonResponse(wings_data, safe=False)

@login_required
def branch_wise_report_view(request):
    """Branch wise report view"""
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    selected_branch = request.GET.get('branch')
    
    # Base queryset
    branches_queryset = Branch.objects.all().select_related('region', 'region__division_id')
    
    # Apply filters
    if selected_division:
        try:
            division = Division.objects.get(id=selected_division)
            regions_in_division = Region.objects.filter(
                division_id=division
            ).values_list('id', flat=True)
            
            branches_queryset = branches_queryset.filter(region__id__in=regions_in_division)
        except (ValueError, TypeError, Division.DoesNotExist):
            branches_queryset = Branch.objects.none()

    if selected_region:
        try:
            region = Region.objects.get(name=selected_region)
            branches_queryset = branches_queryset.filter(region=region)
        except (ValueError, TypeError, Region.DoesNotExist):
            branches_queryset = Branch.objects.none()
            
    if selected_branch:
        try:
            branch = Branch.objects.get(id=selected_branch)
            branches_queryset = branches_queryset.filter(id=branch.id)
        except (ValueError, TypeError, Branch.DoesNotExist):
            branches_queryset = Branch.objects.none()
    
    # Calculate metrics
    total_branches = branches_queryset.count()
    
    # Prepare branch data
    branch_data = []
    total_employees = 0
    
    for branch in branches_queryset:
        # Get employees for this branch
        branch_employees = Employee.objects.filter(branch=branch, is_active=True)
        employee_count = branch_employees.count()
        total_employees += employee_count
        
        # Calculate designation distribution
        designation_distribution = {}
        for employee in branch_employees:
            if employee.designation:
                designation_title = employee.designation.title
                if designation_title in designation_distribution:
                    designation_distribution[designation_title] += 1
                else:
                    designation_distribution[designation_title] = 1
        
        # Calculate grade distribution
        grade_distribution = {}
        for employee in branch_employees:
            if employee.employee_grade:
                grade_name = employee.employee_grade.grade_name
                if grade_name in grade_distribution:
                    grade_distribution[grade_name] += 1
                else:
                    grade_distribution[grade_name] = 1
        
        # Calculate gender distribution based on CNIC number
        gender_distribution = calculate_gender_distribution(branch_employees)
        
        branch_info = {
            'id': branch.id,
            'branch_name': branch.branch_name,
            'region': branch.region.name if branch.region else 'N/A',
            'division': branch.region.division_id.division_name if branch.region and branch.region.division_id else 'N/A',
            'employee_count': employee_count,
            'designation_counts': [{'designation__title': title, 'count': count} for title, count in designation_distribution.items()],
            'grade_counts': [{'employee_grade__grade_name': grade, 'count': count} for grade, count in grade_distribution.items()],
            'gender_distribution': gender_distribution,
        }
        branch_data.append(branch_info)
    
    # Calculate average employees per branch
    avg_employees_per_branch = total_employees / total_branches if total_branches > 0 else 0
    
    # Pagination
    paginator = Paginator(branch_data, 25)  # Show 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'total_branches': total_branches,
        'total_employees': total_employees,
        'avg_employees_per_branch': round(avg_employees_per_branch, 2),
        'branch_data': page_obj,
        'divisions': list(Division.objects.all()),
        'regions': list(Region.objects.all()),
        'branches': list(Branch.objects.all()),
        'selected_division': selected_division,
        'selected_region': selected_region,
        'selected_branch': selected_branch,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }
    return render(request, 'analytics/branch_wise_report.html', context)

@login_required
def wing_wise_report_view(request):
    """Wing wise report view"""
    selected_division = request.GET.get('division')
    selected_wing = request.GET.get('wing')
    
    # Base queryset
    wings_queryset = Wing.objects.all().select_related('division_id')
    
    # Apply filters
    if selected_division:
        try:
            division = Division.objects.get(id=selected_division)
            wings_queryset = wings_queryset.filter(division_id=division)
        except (ValueError, TypeError, Division.DoesNotExist):
            wings_queryset = Wing.objects.none()
            
    if selected_wing:
        try:
            wing = Wing.objects.get(id=selected_wing)
            wings_queryset = wings_queryset.filter(id=wing.id)
        except (ValueError, TypeError, Wing.DoesNotExist):
            wings_queryset = Wing.objects.none()
    
    # Calculate metrics
    total_wings = wings_queryset.count()
    
    # Prepare wing data
    wing_data = []
    total_employees = 0
    
    for wing in wings_queryset:
        # Get employees for this wing
        wing_employees = Employee.objects.filter(wing=wing, is_active=True, branch__isnull=True)
        employee_count = wing_employees.count()
        total_employees += employee_count
        
        # Calculate designation distribution
        designation_distribution = {}
        for employee in wing_employees:
            if employee.designation:
                designation_title = employee.designation.title
                if designation_title in designation_distribution:
                    designation_distribution[designation_title] += 1
                else:
                    designation_distribution[designation_title] = 1
        
        # Calculate grade distribution
        grade_distribution = {}
        for employee in wing_employees:
            if employee.employee_grade:
                grade_name = employee.employee_grade.grade_name
                if grade_name in grade_distribution:
                    grade_distribution[grade_name] += 1
                else:
                    grade_distribution[grade_name] = 1
        
        # Calculate gender distribution based on CNIC number
        gender_distribution = calculate_gender_distribution(wing_employees)
        
        wing_info = {
            'id': wing.id,
            'wing_name': wing.name,
            'division_id': wing.division_id,
            'employee_count': employee_count,
            'designation_counts': [{'designation__title': title, 'count': count} for title, count in designation_distribution.items()],
            'grade_counts': [{'employee_grade__grade_name': grade, 'count': count} for grade, count in grade_distribution.items()],
            'gender_distribution': gender_distribution,
        }
        wing_data.append(wing_info)
    
    # Calculate average employees per wing
    avg_employees_per_wing = total_employees / total_wings if total_wings > 0 else 0
    
    # Pagination
    paginator = Paginator(wing_data, 25)  # Show 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'total_wings': total_wings,
        'total_employees': total_employees,
        'avg_employees_per_wing': round(avg_employees_per_wing, 2),
        'wing_data': page_obj,
        'divisions': list(Division.objects.all()),
        'wings': list(Wing.objects.all()),
        'selected_division': selected_division,
        'selected_wing': selected_wing,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }
    return render(request, 'analytics/wing_wise_report.html', context)

@login_required
def division_wise_report_view(request):
    """Division Wise Report View"""
    # Get filter parameters
    selected_division = request.GET.get('division')
    
    # Initialize base querysets
    divisions_queryset = Division.objects.all().order_by('division_name')
    employees_queryset = Employee.objects.filter(is_active=True).select_related('region', 'branch', 'designation', 'employee_grade')
    
    # Apply filters if provided
    if selected_division:
        try:
            division_name = int(selected_division)
            divisions_queryset = divisions_queryset.filter(id=division_name)
            
            # Get regions in this division
            regions_in_division = Region.objects.filter(division_id=division_name).values_list('id', flat=True)
            employees_queryset = employees_queryset.filter(region_id__in=regions_in_division)
        except (ValueError, TypeError):
            divisions_queryset = Division.objects.none()
            employees_queryset = Employee.objects.none()
    
    # Prepare division data
    division_data = []
    for division in divisions_queryset:
        # Get regions in this division
        regions = Region.objects.filter(division_id=division.id)
        region_ids = regions.values_list('id', flat=True)
        
        # Get branches in these regions
        branches = Branch.objects.filter(region__id__in=region_ids)
        branch_count = branches.count()
        
        # Get employees in these regions
        division_employees = employees_queryset.filter(region_id__in=region_ids)
        employee_count = division_employees.count()
        
        # Calculate designation distribution
        designation_counts = division_employees.values('designation__title').annotate(count=Count('SAP_ID'))
        
        # Calculate grade distribution
        grade_counts = division_employees.values('employee_grade__grade_name').annotate(count=Count('SAP_ID'))
        
        # Calculate gender distribution based on CNIC number
        gender_distribution = calculate_gender_distribution(division_employees)
        
        division_info = {
            'id': division.id,
            'name': division.division_name,
            'region_count': regions.count(),
            'branch_count': branch_count,
            'employee_count': employee_count,
            'designation_counts': list(designation_counts),
            'grade_counts': list(grade_counts),
            'gender_distribution': gender_distribution,
        }
        division_data.append(division_info)
    
    # Pagination
    paginator = Paginator(division_data, 10)  # Show 10 divisions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'division_count': divisions_queryset.count(),
        'total_employees': employees_queryset.count(),
        'division_data': page_obj,
        'divisions': list(Division.objects.all().order_by('division_name')),
        'selected_division': selected_division,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }
    return render(request, 'analytics/division_wise_report.html', context)

@login_required
def region_wise_report_view(request):
    """Region Wise Report View"""
    # Get filter parameters
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    
    # Initialize base querysets
    regions_queryset = Region.objects.all().select_related('division_id').order_by('name')
    employees_queryset = Employee.objects.filter(is_active=True).select_related('region', 'branch', 'designation', 'employee_grade')
    
    # Apply filters if provided
    if selected_division:
        try:
            division_name = int(selected_division)
            regions_queryset = regions_queryset.filter(division_id=division_name)
            
            # Get regions in this division
            region_ids = regions_queryset.values_list('id', flat=True)
            employees_queryset = employees_queryset.filter(region_id__in=region_ids)
        except (ValueError, TypeError):
            regions_queryset = Region.objects.none()
            employees_queryset = Employee.objects.none()
    
    if selected_region:
        try:
            region_id = int(selected_region)
            regions_queryset = regions_queryset.filter(id=region_id)
            employees_queryset = employees_queryset.filter(region_id=region_id)
        except (ValueError, TypeError):
            regions_queryset = Region.objects.none()
            employees_queryset = Employee.objects.none()
    
    # Prepare region data
    region_data = []
    for region in regions_queryset:
        # Get branches in this region
        branches = Branch.objects.filter(region=region)
        branch_count = branches.count()
        
        # Get employees in this region
        region_employees = employees_queryset.filter(region=region)
        employee_count = region_employees.count()
        
        # Calculate designation distribution
        designation_counts = region_employees.values('designation__title').annotate(count=Count('SAP_ID'))
        
        # Calculate grade distribution
        grade_counts = region_employees.values('employee_grade__grade_name').annotate(count=Count('SAP_ID'))
        
        # Calculate gender distribution based on CNIC number
        gender_distribution = calculate_gender_distribution(region_employees)
        
        region_info = {
            'id': region.id,
            'name': region.name,
            'division': region.division_id.division_name if region.division_id else 'N/A',
            'branch_count': branch_count,
            'employee_count': employee_count,
            'designation_counts': list(designation_counts),
            'grade_counts': list(grade_counts),
            'gender_distribution': gender_distribution,
        }
        region_data.append(region_info)
    
    # Pagination
    paginator = Paginator(region_data, 10)  # Show 10 regions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'region_count': regions_queryset.count(),
        'total_employees': employees_queryset.count(),
        'region_data': page_obj,
        'divisions': list(Division.objects.all().order_by('division_name')),
        'regions': list(Region.objects.all().order_by('name')),
        'selected_division': selected_division,
        'selected_region': selected_region,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }
    return render(request, 'analytics/region_wise_report.html', context)

@login_required
def ho_report_view(request):
    """Head Office Report View"""
    # Get filter parameters
    selected_wing = request.GET.get('wing')
    
    # Initialize base querysets - filter for HO employees (those not assigned to branches)
    ho_employees = Employee.objects.filter(
        is_active=True,
        branch__isnull=True  # Employees not assigned to any branch are considered HO employees
    ).select_related('wing', 'designation', 'employee_grade')
    
    wings_queryset = Wing.objects.all().order_by('name')
    
    # Apply filters if provided
    if selected_wing:
        try:
            wing_id = int(selected_wing)
            ho_employees = ho_employees.filter(wing_id=wing_id)
            wings_queryset = wings_queryset.filter(id=wing_id)
        except (ValueError, TypeError):
            ho_employees = Employee.objects.none()
            wings_queryset = Wing.objects.none()
    
    # Calculate metrics
    total_ho_employees = ho_employees.count()
    
    # Calculate designation distribution
    designation_counts = ho_employees.values('designation__title').annotate(count=Count('SAP_ID'))
    
    # Calculate grade distribution
    grade_counts = ho_employees.values('employee_grade__grade_name').annotate(count=Count('SAP_ID'))
    
    # Calculate gender distribution based on CNIC number
    gender_distribution = calculate_gender_distribution(ho_employees)
     
     # Calculate wing distribution
    wing_distribution = ho_employees.values('wing__name').annotate(count=Count('SAP_ID'))
     
     # Prepare employee data for table
    employee_data = []
    for employee in ho_employees:
        emp_data = {
            'sap_id': employee.SAP_ID,
            'name': employee.name,
            'designation': employee.designation.title if employee.designation else 'N/A',
            'wing': employee.wing.name if employee.wing else 'N/A',
            'grade': employee.employee_grade.grade_name if employee.employee_grade else 'N/A',
            'gender': employee.gender,
            'date_of_joining': employee.date_of_joining,
            'date_of_birth': employee.date_of_birth,
        }
        employee_data.append(emp_data)
    
    # Pagination
    paginator = Paginator(employee_data, 25)  # Show 25 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'total_ho_employees': total_ho_employees,
        'designation_counts': list(designation_counts),
        'grade_counts': list(grade_counts),
        'gender_distribution': gender_distribution,
        'wing_distribution': list(wing_distribution),
        'employee_data': page_obj,
        'wings': list(Wing.objects.all().order_by('name')),
        'selected_wing': selected_wing,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }
    return render(request, 'analytics/ho_report.html', context)

@login_required
def reo_report_view(request):
    """Regional Operations Executive report view"""
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    
    # Base queryset
    reo_queryset = Employee.objects.filter(
        designation__title__icontains='RE OPS',
        is_active=True
    ).select_related('region', 'designation', 'employee_grade')
    
    regions_queryset = Region.objects.all()

    # Apply filters
    if selected_division:
        try:
            division = Division.objects.get(division_name=selected_division)
            regions_in_division = Region.objects.filter(
                division_id=division
            ).values_list('name', flat=True)
            
            reo_queryset = reo_queryset.filter(region__name__in=regions_in_division)
            regions_queryset = regions_queryset.filter(name__in=regions_in_division)
        except (ValueError, TypeError, Division.DoesNotExist):
            reo_queryset = Employee.objects.none()
            regions_queryset = Region.objects.none()

    if selected_region:
        try:
            region = Region.objects.get(name=selected_region)
            reo_queryset = reo_queryset.filter(region=region)
            regions_queryset = regions_queryset.filter(name=region.name)
        except (ValueError, TypeError, Region.DoesNotExist):
            reo_queryset = Employee.objects.none()
            regions_queryset = Region.objects.none()

    # Calculate metrics
    total_reo = reo_queryset.count()
    regions_with_reo = regions_queryset.filter(
        name__in=reo_queryset.values_list('region__name', flat=True).distinct()
    )
    
    # Current year calculations
    current_year = timezone.now().year
    current_year_str = str(current_year)
    
    # APA Grading distribution
    grade_distribution = {
        'Excellent': reo_queryset.filter(grade_assignment='Excellent').count(),
        'Very Good': reo_queryset.filter(grade_assignment='Very Good').count(),
        'Good': reo_queryset.filter(grade_assignment='Good').count(),
        'Needs Improvement': reo_queryset.filter(grade_assignment='Needs Improvement').count(),
        'Unsatisfactory': reo_queryset.filter(grade_assignment='Unsatisfactory').count(),
        'Not Assigned': reo_queryset.filter(grade_assignment='Not Assigned').count(),
    }
    
    # Calculate gender distribution based on CNIC number
    gender_distribution = calculate_gender_distribution(reo_queryset)

    # Prepare region data
    region_reo_data = []
    for region in regions_queryset:
        region_reo = reo_queryset.filter(region=region).first()
        
        region_data = {
            'region_id': region.region_id if region.region_id else 'N/A',
            'region_name': region.name,
            'division': region.division_id.division_name if region.division_id else 'N/A',
            'reo_assigned': bool(region_reo),
            'assigned_person': region_reo.name if region_reo else None,
            'grade': region_reo.employee_grade.grade_name if region_reo and region_reo.employee_grade else None,
            'status': 'Upgraded' if region_reo and region_reo.date_of_joining and current_year_str in region_reo.date_of_joining else None,
            'branch_count': Branch.objects.filter(region=region).count()
        }
        region_reo_data.append(region_data)
    
    context = {
        'total_reo': total_reo,
        'regions_with_reo': regions_with_reo.count(),
        'regions_without_reo': regions_queryset.count() - regions_with_reo.count(),
        'upgraded_to_reo': reo_queryset.filter(date_of_joining__contains=current_year_str).count(),
        'grade_distribution': grade_distribution,
        'gender_distribution': gender_distribution,
        'region_reo_data': region_reo_data,
        'divisions': list(Division.objects.all()),
        'regions': list(Region.objects.all()),
        'selected_division': selected_division,
        'selected_region': selected_region,
    }
    return render(request, 'analytics/reo_report.html', context)

@login_required
def reic_report_view(request):
    """Regional Incharge report view"""
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    
    # Base queryset
    reic_queryset = Employee.objects.filter(
        designation__title__icontains='RE IC',
        is_active=True
    ).select_related('region', 'designation', 'employee_grade')
    
    regions_queryset = Region.objects.all()

    # Apply filters
    if selected_division:
        try:
            division = Division.objects.get(division_name=selected_division)
            regions_in_division = Region.objects.filter(
                division_id=division
            ).values_list('name', flat=True)
            
            reic_queryset = reic_queryset.filter(region__name__in=regions_in_division)
            regions_queryset = regions_queryset.filter(name__in=regions_in_division)
        except (ValueError, TypeError, Division.DoesNotExist):
            reic_queryset = Employee.objects.none()
            regions_queryset = Region.objects.none()

    if selected_region:
        try:
            region = Region.objects.get(name=selected_region)
            reic_queryset = reic_queryset.filter(region=region)
            regions_queryset = regions_queryset.filter(name=region.name)
        except (ValueError, TypeError, Region.DoesNotExist):
            reic_queryset = Employee.objects.none()
            regions_queryset = Region.objects.none()

    # Calculate metrics
    total_reic = reic_queryset.count()
    regions_with_reic = regions_queryset.filter(
        name__in=reic_queryset.values_list('region__name', flat=True).distinct()
    )
    
    # Current year calculations
    current_year = timezone.now().year
    current_year_str = str(current_year)
    
    # APA Grading distribution
    grade_distribution = {
        'Excellent': reic_queryset.filter(grade_assignment='Excellent').count(),
        'Very Good': reic_queryset.filter(grade_assignment='Very Good').count(),
        'Good': reic_queryset.filter(grade_assignment='Good').count(),
        'Needs Improvement': reic_queryset.filter(grade_assignment='Needs Improvement').count(),
        'Unsatisfactory': reic_queryset.filter(grade_assignment='Unsatisfactory').count(),
        'Not Assigned': reic_queryset.filter(grade_assignment='Not Assigned').count(),
    }

    # Prepare region data
    region_reic_data = []
    for region in regions_queryset:
        region_reic = reic_queryset.filter(region=region).first()
        
        region_data = {
            'region_id': region.region_id if region.region_id else 'N/A',
            'region_name': region.name,
            'division': region.division_id.division_name if region.division_id else 'N/A',
            'reic_assigned': bool(region_reic),
            'assigned_person': region_reic.name if region_reic else None,
            'grade': region_reic.employee_grade.grade_name if region_reic and region_reic.employee_grade else None,
            'status': 'Upgraded' if region_reic and region_reic.date_of_joining and current_year_str in region_reic.date_of_joining else None,
            'branch_count': Branch.objects.filter(region=region).count()
        }
        region_reic_data.append(region_data)
    
    # Calculate age distribution (mock data for now)
    age_distribution = {
        '20-30': total_reic // 4,
        '31-40': total_reic // 4,
        '41-50': total_reic // 4,
        '51+': total_reic - 3*(total_reic // 4)
    }
    
    # Calculate gender distribution based on CNIC number
    gender_distribution = calculate_gender_distribution(reic_queryset)
    
    # Calculate staff downgraded from REIC (mock data for now)
    staff_downgraded_from_reic = 0
    
    # Calculate average years as REIC (mock data for now)
    avg_years_as_reic = 3

    # Pagination
    paginator = Paginator(region_reic_data, 25)  # Show 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'total_reic': total_reic,
        'regions_with_reic': regions_with_reic.count(),
        'regions_without_reic': regions_queryset.count() - regions_with_reic.count(),
        'staff_upgraded_to_reic': reic_queryset.filter(date_of_joining__contains=current_year_str).count(),
        'staff_downgraded_from_reic': staff_downgraded_from_reic,
        'avg_years_as_reic': avg_years_as_reic,
        'age_distribution': age_distribution,
        'gender_distribution': gender_distribution,
        'grade_distribution': grade_distribution,
        'region_reic_data': region_reic_data,
        'divisions': list(Division.objects.all()),
        'regions': list(Region.objects.all()),
        'selected_division': selected_division,
        'selected_region': selected_region,
        'region_reic_data': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }
    return render(request, 'analytics/reic_report.html', context)

@login_required
def api_regions(request):
    """API endpoint to get regions filtered by division"""
    division_name = request.GET.get('division')
    
    regions = Region.objects.all()
    if division_name:
        try:
            division = Division.objects.get(id=division_name)
            regions = regions.filter(division_id=division)
        except (ValueError, TypeError, Division.DoesNotExist):
            return JsonResponse([], safe=False)
    
    regions_data = [{'id': region.id, 'name': region.name} for region in regions]
    return JsonResponse(regions_data, safe=False)

@login_required
def api_branches(request):
    """API endpoint to get branches filtered by region"""
    region_id = request.GET.get('region')
    
    branches = Branch.objects.all()
    if region_id:
        try:
            region = Region.objects.get(id=region_id)
            branches = branches.filter(region=region)
        except (ValueError, TypeError, Region.DoesNotExist):
            return JsonResponse([], safe=False)
    
    branches_data = [{'id': branch.id, 'branch_name': branch.branch_name} for branch in branches]
    return JsonResponse(branches_data, safe=False)