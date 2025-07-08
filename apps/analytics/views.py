from django.shortcuts import render
from django.db.models import Count, Avg, F, Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.HRIS_App.models import Employee, Branch, Region, Division, Wing, Designation, Cadre, EmployeeType, EmployeeGrade, Qualification, APA_Grading
from django.core.paginator import Paginator

def calculate_gender_distribution(employees_queryset):
    """Calculate gender distribution based on CNIC number"""
    male_count = 0
    female_count = 0
    other_count = 0
    for employee in employees_queryset:
        if employee.cnic_no and len(employee.cnic_no) > 0:
            try:
                last_digit = int(employee.cnic_no[-1])
                if last_digit % 2 == 0:
                    female_count += 1
                else:
                    male_count += 1
            except (ValueError, IndexError):
                other_count += 1
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
    # Optimize queries with select_related to reduce database hits
    active_employees = Employee.objects.filter(is_active=True)
    
    bom_employees = active_employees.filter(designation__title__icontains='Branch Operations Manager').select_related('branch', 'region', 'designation', 'employee_grade')
    re_ops_employees = active_employees.filter(designation__title__icontains='RE OPS').select_related('branch', 'region', 'designation', 'employee_grade')
    re_ic_employees = active_employees.filter(designation__title__icontains='RE IC').select_related('branch', 'region', 'designation', 'employee_grade')

    # Get designation counts with optimized query
    designation_counts = active_employees.values('designation__title')\
        .annotate(count=Count('id'))\
        .filter(count__gt=0)\
        .order_by('-count')

    context = {
        'branch_count': Branch.objects.count(),
        'region_count': Region.objects.count(),
        'division_count': Division.objects.count(),
        'wing_count': Wing.objects.count(),
        'employee_count': active_employees.count(),
        'designation_counts': designation_counts,
        'bom_employees': bom_employees,
        're_ops_employees': re_ops_employees,
        're_ic_employees': re_ic_employees,
    }

    return render(request, 'analytics/analytics.html', context)

@login_required
def bom_report_view(request):
    """Branch Operations Manager report view"""
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    selected_branch = request.GET.get('branch')

    # Base querysets with optimized select_related
    bom_queryset = Employee.objects.filter(designation__title__icontains='Branch Operations Manager', is_active=True).select_related('branch', 'region', 'designation', 'employee_grade')
    branches_queryset = Branch.objects.all().select_related('region')

    # Apply filters if selected
    if selected_division:
        # Since Region doesn't have division_id field, we can't filter by division
        # Keep all regions when division is selected
        pass

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

    # Fetch all data at once to minimize database hits
    bom_list = list(bom_queryset)
    branches_list = list(branches_queryset)

    # Calculate KPI metrics
    total_bom = len(bom_list)
    branch_names_with_bom = {bom.branch.branch_name for bom in bom_list if bom.branch}
    branches_with_bom = [branch for branch in branches_list if branch.branch_name in branch_names_with_bom]
    branches_with_bom_count = len(branches_with_bom)

    # More calculations...
    gender_distribution = calculate_gender_distribution(bom_list)

    context = {
        'total_bom': total_bom,
        'branches_with_bom': branches_with_bom_count,
        'branches_without_bom': len(branches_list) - branches_with_bom_count,
        'gender_distribution': gender_distribution,
        # More context variables...
    }

    return render(request, 'analytics/bom_report.html', context)

@login_required
def api_regions(request):
    """API endpoint to get regions filtered by division"""
    division_name = request.GET.get('division')
    regions = Region.objects.all()

    if division_name:
        # Since Region doesn't have division_id field, we can't filter by division
        # Return all regions when division is selected
        pass

    regions_data = [{'id': region.id, 'name': region.name} for region in regions]
    return JsonResponse(regions_data, safe=False)

@login_required
def api_branches(request):
    """API endpoint to get branches filtered by region"""
    region_id = request.GET.get('region')
    branches = Branch.objects.all().select_related('region')

    if region_id:
        try:
            region_id = int(region_id)
            branches = branches.filter(region_id=region_id)
        except (ValueError, TypeError):
            return JsonResponse([], safe=False)

    branches_data = [{'id': branch.id, 'branch_name': branch.branch_name} for branch in branches]
    return JsonResponse(branches_data, safe=False)

@login_required
def branch_wise_report_view(request):
    """Branch wise report view"""
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')
    selected_branch = request.GET.get('branch')

    # Base queryset with optimized select_related
    branches_queryset = Branch.objects.all().select_related('region')

    # Apply filters if selected
    if selected_division:
        # Since Region doesn't have division_id field, we can't filter by division
        # Keep all branches when division is selected
        pass

    if selected_region:
        try:
            region_id = int(selected_region)
            branches_queryset = branches_queryset.filter(region_id=region_id)
        except (ValueError, TypeError):
            branches_queryset = Branch.objects.none()

    if selected_branch:
        try:
            branch_id = int(selected_branch)
            branches_queryset = branches_queryset.filter(id=branch_id)
        except (ValueError, TypeError):
            branches_queryset = Branch.objects.none()

    # Fetch all branches at once to minimize database hits
    branches_list = list(branches_queryset)
    total_branches = len(branches_list)

    # Get all branch IDs for employee query
    branch_ids = [branch.id for branch in branches_list]

    # Get all employees for these branches in a single query with all needed relations
    all_branch_employees = list(Employee.objects.filter(branch__id__in=branch_ids, is_active=True).select_related('designation', 'employee_grade', 'branch'))

    # Group employees by branch for efficient lookup
    branch_employee_map = {}
    for employee in all_branch_employees:
        if employee.branch_id not in branch_employee_map:
            branch_employee_map[employee.branch_id] = []
        branch_employee_map[employee.branch_id].append(employee)

    # Calculate total employees once
    total_employees = len(all_branch_employees)

    # Prepare branch data
    branch_data = []
    for branch in branches_list:
        branch_employees = branch_employee_map.get(branch.id, [])
        employee_count = len(branch_employees)

        # Calculate all distributions in a single pass
        designation_distribution = {}
        grade_distribution = {}
        for employee in branch_employees:
            if employee.designation:
                designation_title = employee.designation.title
                designation_distribution[designation_title] = designation_distribution.get(designation_title, 0) + 1

            if employee.employee_grade:
                grade_name = employee.employee_grade.grade_name
                grade_distribution[grade_name] = grade_distribution.get(grade_name, 0) + 1

        # Convert dictionaries to sorted lists of dictionaries
        designation_counts_list = [{'designation__title': title, 'count': count} for title, count in sorted(designation_distribution.items())]
        grade_counts_list = [{'employee_grade__grade_name': grade, 'count': count} for grade, count in sorted(grade_distribution.items())]

        # Calculate gender distribution
        gender_distribution = calculate_gender_distribution(branch_employees)

        branch_info = {
            'id': branch.id,
            'branch_name': branch.branch_name,
            'region': branch.region.name if branch.region else 'N/A',
            'division': 'N/A',  # Division is not directly accessible from region
            'employee_count': employee_count,
            'designation_counts': designation_counts_list,
            'grade_counts': grade_counts_list,
            'gender_distribution': gender_distribution,
        }
        branch_data.append(branch_info)

    # Calculate average employees per branch
    avg_employees_per_branch = total_employees / total_branches if total_branches > 0 else 0

    # Pagination
    paginator = Paginator(branch_data, 25)  # Show 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prefetch all divisions, regions, and branches for dropdowns to avoid N+1 queries
    all_divisions = list(Division.objects.all().order_by('division_name'))
    all_regions = list(Region.objects.all().order_by('name'))
    all_branches = list(Branch.objects.all().order_by('branch_name'))

    context = {
        'total_branches': total_branches,
        'total_employees': total_employees,
        'avg_employees_per_branch': round(avg_employees_per_branch, 2),
        'branch_data': page_obj,
        'divisions': all_divisions,
        'regions': all_regions,
        'branches': all_branches,
        'selected_division': selected_division,
        'selected_region': selected_region,
        'selected_branch': selected_branch,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }

    return render(request, 'analytics/branch_wise_report.html', context)

# Repeat similar changes to other views where `select_related` and foreign key relationships are used (Wing, Region, etc.)
@login_required
def wing_wise_report_view(request):
    """Wing wise report view"""
    selected_division = request.GET.get('division')
    selected_wing = request.GET.get('wing')

    # Base queryset with optimized select_related
    wings_queryset = Wing.objects.all().select_related('division_name')

    # Apply filters if selected
    if selected_division:
        try:
            division_id = int(selected_division)
            wings_queryset = wings_queryset.filter(division_name_id=division_id)
        except (ValueError, TypeError):
            wings_queryset = Wing.objects.none()

    if selected_wing:
        try:
            wing_id = int(selected_wing)
            wings_queryset = wings_queryset.filter(id=wing_id)
        except (ValueError, TypeError):
            wings_queryset = Wing.objects.none()

    # Fetch all wings at once to minimize database hits
    wings_list = list(wings_queryset)
    total_wings = len(wings_list)

    # Get all wing IDs to fetch employees in a single query
    wing_ids = [wing.id for wing in wings_list]

    # Fetch all employees for these wings in a single query with all needed relations
    all_wing_employees = list(Employee.objects.filter(wing_id__in=wing_ids, is_active=True, branch__isnull=True).select_related('designation', 'employee_grade', 'wing'))

    # Group employees by wing for efficient lookup
    wing_employee_map = {}
    for employee in all_wing_employees:
        if employee.wing_id not in wing_employee_map:
            wing_employee_map[employee.wing_id] = []
        wing_employee_map[employee.wing_id].append(employee)

    # Calculate total employees once
    total_employees = len(all_wing_employees)

    # Prepare wing data
    wing_data = []
    for wing in wings_list:
        wing_employees = wing_employee_map.get(wing.id, [])
        employee_count = len(wing_employees)

        # Calculate all distributions in a single pass
        designation_distribution = {}
        grade_distribution = {}
        for employee in wing_employees:
            if employee.designation:
                designation_title = employee.designation.title
                designation_distribution[designation_title] = designation_distribution.get(designation_title, 0) + 1

            if employee.employee_grade:
                grade_name = employee.employee_grade.grade_name
                grade_distribution[grade_name] = grade_distribution.get(grade_name, 0) + 1

        # Convert dictionaries to sorted lists of dictionaries
        designation_counts_list = [{'designation__title': title, 'count': count} for title, count in sorted(designation_distribution.items())]
        grade_counts_list = [{'employee_grade__grade_name': grade, 'count': count} for grade, count in sorted(grade_distribution.items())]

        # Calculate gender distribution
        gender_distribution = calculate_gender_distribution(wing_employees)

        wing_info = {
            'id': wing.id,
            'wing_name': wing.name,
            'division_id': wing.division_name_id,
            'employee_count': employee_count,
            'designation_counts': designation_counts_list,
            'grade_counts': grade_counts_list,
            'gender_distribution': gender_distribution,
        }
        wing_data.append(wing_info)

    # Calculate average employees per wing
    avg_employees_per_wing = total_employees / total_wings if total_wings > 0 else 0

    # Pagination
    paginator = Paginator(wing_data, 25)  # Show 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prefetch all divisions and wings for dropdowns to avoid N+1 queries
    all_divisions = list(Division.objects.all().order_by('division_name'))
    all_wings = list(Wing.objects.all().order_by('name'))

    context = {
        'total_wings': total_wings,
        'total_employees': total_employees,
        'avg_employees_per_wing': round(avg_employees_per_wing, 2),
        'wing_data': page_obj,
        'divisions': all_divisions,
        'wings': all_wings,
        'selected_division': selected_division,
        'selected_wing': selected_wing,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }

    return render(request, 'analytics/wing_wise_report.html', context)

@login_required
def division_wise_report_view(request):
    """Division Wise Report View"""
    selected_division = request.GET.get('division')
    
    # Initialize base querysets with optimized queries
    divisions_queryset = Division.objects.all().order_by('division_name')
    
    # Apply filters if provided
    if selected_division:
        try:
            division_id = int(selected_division)
            divisions_queryset = divisions_queryset.filter(id=division_id)
        except (ValueError, TypeError):
            divisions_queryset = Division.objects.none()

    # Prepare division data
    division_data = []
    
    # Prefetch all regions for these divisions in a single query
    all_division_ids = list(divisions_queryset.values_list('id', flat=True))
    # Since Region doesn't have division_id field, we can't filter by it
    all_regions = Region.objects.all()

    # Since Region doesn't have division_id field, we can't group by division
    # Create a default group for all regions
    regions_by_division = {}
    for division in divisions_queryset:
        regions_by_division[division.id] = list(all_regions)

    # Get all region IDs
    all_region_ids = [region.id for region in all_regions]

    # Prefetch all branches for these regions in a single query
    all_branches = Branch.objects.filter(region_id__in=all_region_ids)

    # Group branches by region
    branches_by_region = {}
    for branch in all_branches:
        if branch.region_id not in branches_by_region:
            branches_by_region[branch.region_id] = []
        branches_by_region[branch.region_id].append(branch)

    # Get all employees for these regions in a single query
    all_employees = Employee.objects.filter(region_id__in=all_region_ids, is_active=True).select_related('designation', 'employee_grade')

    # Group employees by region for efficient access
    employees_by_region = {}
    for employee in all_employees:
        if employee.region_id not in employees_by_region:
            employees_by_region[employee.region_id] = []
        employees_by_region[employee.region_id].append(employee)

    for division in divisions_queryset:
        # Get regions in this division
        division_regions = regions_by_division.get(division.id, [])
        region_count = len(division_regions)
        region_ids = [region.id for region in division_regions]

        # Get branches in these regions
        branch_count = 0
        for region_id in region_ids:
            branch_count += len(branches_by_region.get(region_id, []))

        # Get employees in these regions
        division_employees = []
        for region_id in region_ids:
            division_employees.extend(employees_by_region.get(region_id, []))
        employee_count = len(division_employees)

        # Calculate designation distribution
        designation_counts = {}
        for employee in division_employees:
            if employee.designation:
                title = employee.designation.title
                designation_counts[title] = designation_counts.get(title, 0) + 1
        designation_counts_list = [{'designation__title': title, 'count': count} for title, count in designation_counts.items()]

        # Calculate grade distribution
        grade_counts = {}
        for employee in division_employees:
            if employee.employee_grade:
                grade = employee.employee_grade.grade_name
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        grade_counts_list = [{'employee_grade__grade_name': grade, 'count': count} for grade, count in grade_counts.items()]

        # Calculate gender distribution based on CNIC number
        gender_distribution = calculate_gender_distribution(division_employees)

        division_info = {
            'id': division.id,
            'name': division.division_name,
            'region_count': region_count,
            'branch_count': branch_count,
            'employee_count': employee_count,
            'designation_counts': designation_counts_list,
            'grade_counts': grade_counts_list,
            'gender_distribution': gender_distribution,
        }
        division_data.append(division_info)

    # Pagination
    paginator = Paginator(division_data, 10)  # Show 10 divisions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate total employees once instead of querying again
    total_employees = sum(len(employees) for employees in employees_by_region.values())

    context = {
        'division_count': divisions_queryset.count(),
        'total_employees': total_employees,
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
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')

    # Initialize base querysets
    regions_queryset = Region.objects.all().order_by('name')

    # Apply filters if selected
    if selected_division:
        # Since Region doesn't have division_id field, we can't filter by division
        # Keep all regions when division is selected
        pass

    if selected_region:
        try:
            region_id = int(selected_region)
            regions_queryset = regions_queryset.filter(id=region_id)
        except (ValueError, TypeError):
            regions_queryset = Region.objects.none()

    # Get all region IDs for efficient querying
    region_ids = list(regions_queryset.values_list('id', flat=True))

    # Prefetch all branches for these regions in a single query
    all_branches = Branch.objects.filter(region_id__in=region_ids).select_related('region')

    # Group branches by region for efficient access
    branches_by_region = {}
    for branch in all_branches:
        if branch.region_id not in branches_by_region:
            branches_by_region[branch.region_id] = []
        branches_by_region[branch.region_id].append(branch)

    # Prefetch all employees for these regions in a single query
    all_employees = Employee.objects.filter(region_id__in=region_ids, is_active=True).select_related('region', 'designation', 'employee_grade')

    # Group employees by region for efficient access
    employees_by_region = {}
    for employee in all_employees:
        if employee.region_id not in employees_by_region:
            employees_by_region[employee.region_id] = []
        employees_by_region[employee.region_id].append(employee)

    # Prepare region data
    region_data = []
    for region in regions_queryset:
        # Get branches in this region from our map
        region_branches = branches_by_region.get(region.id, [])
        branch_count = len(region_branches)

        # Get employees in this region from our map
        region_employees = employees_by_region.get(region.id, [])
        employee_count = len(region_employees)

        # Calculate designation distribution
        designation_counts = {}
        for employee in region_employees:
            if employee.designation:
                title = employee.designation.title
                designation_counts[title] = designation_counts.get(title, 0) + 1
        designation_counts_list = [{'designation__title': title, 'count': count} for title, count in designation_counts.items()]

        # Calculate grade distribution
        grade_counts = {}
        for employee in region_employees:
            if employee.employee_grade:
                grade = employee.employee_grade.grade_name
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        grade_counts_list = [{'employee_grade__grade_name': grade, 'count': count} for grade, count in grade_counts.items()]

        # Calculate gender distribution based on CNIC number
        gender_distribution = calculate_gender_distribution(region_employees)

        region_info = {
            'id': region.id,
            'name': region.name,
            'division': 'N/A',  # Division is not directly accessible from region
            'branch_count': branch_count,
            'employee_count': employee_count,
            'designation_counts': designation_counts_list,
            'grade_counts': grade_counts_list,
            'gender_distribution': gender_distribution,
        }
        region_data.append(region_info)

    # Pagination
    paginator = Paginator(region_data, 10)  # Show 10 regions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate total employees once instead of querying again
    total_employees = sum(len(employees) for employees in employees_by_region.values())

    # Prefetch divisions and regions for dropdowns to avoid N+1 queries
    all_divisions = list(Division.objects.all().order_by('division_name'))
    all_regions = list(Region.objects.all().order_by('name'))

    context = {
        'region_count': regions_queryset.count(),
        'total_employees': total_employees,
        'region_data': page_obj,
        'divisions': all_divisions,
        'regions': all_regions,
        'selected_division': selected_division,
        'selected_region': selected_region,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }

    return render(request, 'analytics/region_wise_report.html', context)

@login_required
def ho_report_view(request):
    """Head Office Report View"""
    selected_wing = request.GET.get('wing')

    # Initialize base querysets with optimized select_related
    ho_employees_query = Employee.objects.filter(is_active=True, branch__isnull=True).select_related('wing', 'designation', 'employee_grade')

    # Fetch all wings in a single query
    all_wings = list(Wing.objects.all().select_related('division_name').order_by('name'))

    # Create a map of wing IDs for efficient lookup
    wing_map = {wing.id: wing for wing in all_wings}

    # Apply filters if provided
    if selected_wing:
        try:
            wing_id = int(selected_wing)
            ho_employees_query = ho_employees_query.filter(wing_id=wing_id)
            all_wings = [wing for wing in all_wings if wing.id == wing_id]
        except (ValueError, TypeError):
            ho_employees_query = Employee.objects.none()
            all_wings = []

    # Fetch all employees in a single query
    ho_employees_list = list(ho_employees_query)

    # Calculate total employees once
    total_ho_employees = len(ho_employees_list)

    # Calculate all distributions in a single pass through the data
    designation_counts_dict = {}
    grade_counts_dict = {}
    wing_counts_dict = {}
    employee_data = []

    for employee in ho_employees_list:
        # Designation counts
        if employee.designation:
            title = employee.designation.title
            designation_counts_dict[title] = designation_counts_dict.get(title, 0) + 1

        # Grade counts
        if employee.employee_grade:
            grade = employee.employee_grade.grade_name
            grade_counts_dict[grade] = grade_counts_dict.get(grade, 0) + 1

        # Wing counts
        if employee.wing:
            wing = employee.wing.name
            wing_counts_dict[wing] = wing_counts_dict.get(wing, 0) + 1

        # Prepare employee data for table in the same loop
        try:
            gender = 'Female' if employee.cnic_no and len(employee.cnic_no) > 0 and int(employee.cnic_no[-1]) % 2 == 0 else 'Male'
        except (ValueError, IndexError):
            gender = 'Unknown'

        emp_data = {
            'sap_id': employee.SAP_ID,
            'name': employee.name,
            'designation': employee.designation.title if employee.designation else 'N/A',
            'wing': employee.wing.name if employee.wing else 'N/A',
            'grade': employee.employee_grade.grade_name if employee.employee_grade else 'N/A',
            'gender': gender,
            'date_of_joining': employee.date_of_joining,
            'date_of_birth': employee.birth_date,
        }
        employee_data.append(emp_data)

    # Convert dictionaries to sorted lists for template
    designation_counts = [{'designation__title': title, 'count': count} for title, count in sorted(designation_counts_dict.items(), key=lambda x: x[1], reverse=True)]
    grade_counts = [{'employee_grade__grade_name': grade, 'count': count} for grade, count in sorted(grade_counts_dict.items(), key=lambda x: x[1], reverse=True)]
    wing_distribution = [{'wing__name': wing, 'count': count} for wing, count in sorted(wing_counts_dict.items(), key=lambda x: x[1], reverse=True)]

    # Calculate gender distribution based on CNIC number
    gender_distribution = calculate_gender_distribution(ho_employees_list)

    # Pagination
    paginator = Paginator(employee_data, 25)  # Show 25 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_ho_employees': total_ho_employees,
        'designation_counts': designation_counts,
        'grade_counts': grade_counts,
        'gender_distribution': gender_distribution,
        'wing_distribution': wing_distribution,
        'employee_data': page_obj,
        'wings': all_wings,
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

    # Fetch all divisions and regions in single queries for dropdowns and filtering
    all_divisions = list(Division.objects.all().order_by('division_name'))
    all_regions = list(Region.objects.all().order_by('name'))

    # Create maps for efficient lookups
    division_map = {division.id: division for division in all_divisions}
    region_map = {region.id: region for region in all_regions}

    # Filter regions based on selected division
    regions_queryset = all_regions
    regions_in_division = []
    if selected_division:
        # Since Region doesn't have division_id field, we can't filter by division
        # Keep all regions when division is selected
        pass

    # Further filter by selected region if provided
    if selected_region:
        try:
            region_id = int(selected_region)
            if region_id in region_map:
                regions_queryset = [region for region in regions_queryset if region.id == region_id]
            else:
                regions_queryset = []
        except (ValueError, TypeError):
            regions_queryset = []

    # Get region IDs for filtering
    region_ids = [region.id for region in regions_queryset]

    # Fetch all REOs (Regional Operations Executives) in a single query with all needed relations
    reo_query = Employee.objects.filter(designation__title__icontains='RE OPS', is_active=True)
    
    if region_ids:
        reo_query = reo_query.filter(region_id__in=region_ids)

    # Fetch all data with related objects in a single query
    reo_list = list(reo_query.select_related('region', 'designation', 'employee_grade'))

    # Create a map of regions to REOs for efficient lookup
    reos_by_region = {}
    for employee in reo_list:
        if employee.region_id:
            reos_by_region[employee.region_id] = employee

    # Fetch all branches for these regions in a single query and count by region
    branches = list(Branch.objects.filter(region_id__in=region_ids).values('region_id'))

    # Count branches by region in a single pass
    branch_counts_by_region = {}
    for branch in branches:
        region_id = branch['region_id']
        branch_counts_by_region[region_id] = branch_counts_by_region.get(region_id, 0) + 1

    # Calculate metrics
    total_reo = len(reo_list)
    regions_with_reo_ids = set(reos_by_region.keys())
    regions_with_reo_count = len(regions_with_reo_ids)

    # Current year calculations
    current_year = timezone.now().year
    current_year_str = str(current_year)

    # Count upgraded REOs in a single pass
    upgraded_to_reo_count = sum(1 for employee in reo_list if employee.date_of_joining and current_year_str in employee.date_of_joining)

    # Calculate grade distribution in a single pass
    grade_distribution = {'Excellent': 0, 'Very Good': 0, 'Good': 0, 'Needs Improvement': 0, 'Unsatisfactory': 0, 'Not Assigned': 0}
    for employee in reo_list:
        if employee.grade_assignment in grade_distribution:
            grade_distribution[employee.grade_assignment] += 1

    # Calculate gender distribution based on CNIC number
    gender_distribution = calculate_gender_distribution(reo_list)

    # Prepare region data in a single pass
    region_reo_data = []
    for region in regions_queryset:
        region_reo = reos_by_region.get(region.id)
        region_data = {
            'region_id': region.region_id if region.region_id else 'N/A',
            'region_name': region.name,
            'division': 'N/A',  # Division is not directly accessible from region
            'reo_assigned': bool(region_reo),
            'assigned_person': region_reo.name if region_reo else None,
            'grade': region_reo.employee_grade.grade_name if region_reo and region_reo.employee_grade else None,
            'status': 'Upgraded' if region_reo and region_reo.date_of_joining and current_year_str in region_reo.date_of_joining else None,
            'branch_count': branch_counts_by_region.get(region.id, 0)
        }
        region_reo_data.append(region_data)

    context = {
        'total_reo': total_reo,
        'regions_with_reo': regions_with_reo_count,
        'regions_without_reo': len(regions_queryset) - regions_with_reo_count,
        'upgraded_to_reo': upgraded_to_reo_count,
        'grade_distribution': grade_distribution,
        'gender_distribution': gender_distribution,
        'region_reo_data': region_reo_data,
        'divisions': all_divisions,
        'regions': all_regions,
        'selected_division': selected_division,
        'selected_region': selected_region,
    }

    return render(request, 'analytics/reo_report.html', context)

@login_required
def reic_report_view(request):
    """Regional Incharge report view"""
    selected_division = request.GET.get('division')
    selected_region = request.GET.get('region')

    # Fetch all divisions and regions in single queries for dropdowns and filtering
    all_divisions = list(Division.objects.all().order_by('division_name'))
    all_regions = list(Region.objects.all().order_by('name'))

    # Create maps for efficient lookups
    division_map = {division.id: division for division in all_divisions}
    region_map = {region.id: region for region in all_regions}

    # Filter regions based on selected division
    regions_queryset = all_regions
    regions_in_division = []
    if selected_division:
        # Since Region doesn't have division_id field, we can't filter by division
        # Keep all regions when division is selected
        pass

    # Further filter by selected region if provided
    if selected_region:
        try:
            region_id = int(selected_region)
            if region_id in region_map:
                regions_queryset = [region for region in regions_queryset if region.id == region_id]
            else:
                regions_queryset = []
        except (ValueError, TypeError):
            regions_queryset = []

    # Get region IDs for filtering
    region_ids = [region.id for region in regions_queryset]

    # Fetch all REICs (Regional Incharge) in a single query with all needed relations
    reic_query = Employee.objects.filter(designation__title__icontains='RE IC', is_active=True)

    if region_ids:
        reic_query = reic_query.filter(region_id__in=region_ids)

    # Fetch all data with related objects in a single query
    reic_list = list(reic_query.select_related('region', 'designation', 'employee_grade'))

    # Create a map of regions to REICs for efficient lookup
    reics_by_region = {}
    for employee in reic_list:
        if employee.region_id:
            reics_by_region[employee.region_id] = employee

    # Fetch all branches for these regions in a single query and count by region
    branches = list(Branch.objects.filter(region_id__in=region_ids).values('region_id'))

    # Count branches by region in a single pass
    branch_counts_by_region = {}
    for branch in branches:
        region_id = branch['region_id']
        branch_counts_by_region[region_id] = branch_counts_by_region.get(region_id, 0) + 1

    # Calculate metrics
    total_reic = len(reic_list)
    regions_with_reic_ids = set(reics_by_region.keys())
    regions_with_reic_count = len(regions_with_reic_ids)

    # Current year calculations
    current_year = timezone.now().year
    current_year_str = str(current_year)

    # Count upgraded REICs in a single pass
    upgraded_to_reic_count = sum(1 for employee in reic_list if employee.date_of_joining and current_year_str in employee.date_of_joining)

    # Calculate grade distribution in a single pass
    grade_distribution = {'Excellent': 0, 'Very Good': 0, 'Good': 0, 'Needs Improvement': 0, 'Unsatisfactory': 0, 'Not Assigned': 0}
    for employee in reic_list:
        if employee.grade_assignment in grade_distribution:
            grade_distribution[employee.grade_assignment] += 1

    # Calculate gender distribution based on CNIC number
    gender_distribution = calculate_gender_distribution(reic_list)

    # Prepare region data in a single pass
    region_reic_data = []
    for region in regions_queryset:
        region_reic = reics_by_region.get(region.id)
        region_data = {
            'region_id': region.region_id if region.region_id else 'N/A',
            'region_name': region.name,
            'division': 'N/A',  # Division is not directly accessible from region
            'reic_assigned': bool(region_reic),
            'assigned_person': region_reic.name if region_reic else None,
            'grade': region_reic.employee_grade.grade_name if region_reic and region_reic.employee_grade else None,
            'status': 'Upgraded' if region_reic and region_reic.date_of_joining and current_year_str in region_reic.date_of_joining else None,
            'branch_count': branch_counts_by_region.get(region.id, 0)
        }
        region_reic_data.append(region_data)

    # Calculate age distribution (mock data for now)
    age_distribution = {'20-30': total_reic // 4, '31-40': total_reic // 4, '41-50': total_reic // 4, '51+': total_reic - 3*(total_reic // 4)}

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
        'regions_with_reic': regions_with_reic_count,
        'regions_without_reic': len(regions_queryset) - regions_with_reic_count,
        'staff_upgraded_to_reic': upgraded_to_reic_count,
        'staff_downgraded_from_reic': staff_downgraded_from_reic,
        'avg_years_as_reic': avg_years_as_reic,
        'age_distribution': age_distribution,
        'gender_distribution': gender_distribution,
        'grade_distribution': grade_distribution,
        'region_reic_data': page_obj,
        'divisions': all_divisions,
        'regions': all_regions,
        'selected_division': selected_division,
        'selected_region': selected_region,
        'page_obj': page_obj,
        'is_paginated': paginator.count > paginator.per_page,
    }

    return render(request, 'analytics/reic_report.html', context)
