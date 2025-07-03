from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from HRIS_App.models import (
    Employee,
    EmployeeType,
    Designation,
    EmployeeGrade,
    Branch,
    Region,
    Cadre,
)
from group_head.decorators import admin_or_admin_employee_required
import csv


@login_required(login_url="account:login")
@admin_or_admin_employee_required
def get_filter_counts(request):
    """Get counts for each filter option based on current filter selections"""
    user_region = request.user.region
    user_group = request.user.user_group

    # Base queryset
    employees = Employee.objects.exclude(region__isnull=True, SAP_ID__isnull=True)
    if user_group:
        employees = employees.filter(user_group=user_group)

    # Get all filter parameters
    search_query = request.GET.get("search", "")
    employee_type = request.GET.get("employee_type", "")
    designation = request.GET.get("designation", "")
    employee_grade = request.GET.get("employee_grade", "")
    branch = request.GET.get("branch", "")
    cadre = request.GET.get("cadre", "")
    region = request.GET.get("region", "")

    # Apply filters
    if search_query:
        employees = employees.filter(
            Q(SAP_ID__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
        )
    if employee_type:
        employees = employees.filter(employee_type__name=employee_type)
    if designation:
        employees = employees.filter(designation__title=designation)
    if employee_grade:
        employees = employees.filter(employee_grade__grade_name=employee_grade)
    if branch:
        employees = employees.filter(branch__branch_name__icontains=branch)
    if cadre:
        employees = employees.filter(cadre__name=cadre)
    if region:
        employees = employees.filter(region__name=region)

    # Get counts for each filter type
    employee_type_counts = {}
    designation_counts = {}
    employee_grade_counts = {}
    branch_counts = {}
    cadre_counts = {}
    region_counts = {}

    # Employee Type counts
    if not employee_type:  # Only if not already filtered by employee_type
        type_counts = employees.values("employee_type__name").annotate(
            count=Count("id")
        )
        for item in type_counts:
            if item["employee_type__name"]:
                employee_type_counts[item["employee_type__name"]] = item["count"]

    # Designation counts
    if not designation:  # Only if not already filtered by designation
        des_counts = employees.values("designation__title").annotate(count=Count("id"))
        for item in des_counts:
            if item["designation__title"]:
                designation_counts[item["designation__title"]] = item["count"]

    # Employee Grade counts
    if not employee_grade:  # Only if not already filtered by employee_grade
        grade_counts = employees.values("employee_grade__grade_name").annotate(
            count=Count("id")
        )
        for item in grade_counts:
            if item["employee_grade__grade_name"]:
                employee_grade_counts[item["employee_grade__grade_name"]] = item[
                    "count"
                ]

    # Branch counts
    if not branch:  # Only if not already filtered by branch
        branch_counts_data = employees.values("branch__branch_name").annotate(
            count=Count("id")
        )
        for item in branch_counts_data:
            if item["branch__branch_name"]:
                branch_counts[item["branch__branch_name"]] = item["count"]

    # Cadre counts
    if not cadre:  # Only if not already filtered by cadre
        cadre_counts_data = employees.values("cadre__name").annotate(count=Count("id"))
        for item in cadre_counts_data:
            if item["cadre__name"]:
                cadre_counts[item["cadre__name"]] = item["count"]

    # Region counts
    if not region:  # Only if not already filtered by region
        region_counts_data = employees.values("region__name").annotate(
            count=Count("id")
        )
        for item in region_counts_data:
            if item["region__name"]:
                region_counts[item["region__name"]] = item["count"]

    # Total count after all filters
    total_count = employees.count()

    data = {
        "total_count": total_count,
        "employee_type_counts": employee_type_counts,
        "designation_counts": designation_counts,
        "employee_grade_counts": employee_grade_counts,
        "branch_counts": branch_counts,
        "cadre_counts": cadre_counts,
        "region_counts": region_counts,
    }

    return JsonResponse(data)


@login_required(login_url="account:login")
@admin_or_admin_employee_required
def advanced_search(request):
    """Advanced employee search view with multiple filter options"""
    user_region = request.user.region
    user_group = request.user.user_group

    # Base queryset
    employees = Employee.objects.exclude(region__isnull=True, SAP_ID__isnull=True)
    if user_group:
        employees = employees.filter(user_group=user_group)

    # Get all filter parameters
    search_query = request.GET.get("search", "")
    employee_type = request.GET.get("employee_type", "")
    designation = request.GET.get("designation", "")
    employee_grade = request.GET.get("employee_grade", "")
    branch = request.GET.get("branch", "")
    cadre = request.GET.get("cadre", "")
    region = request.GET.get("region", "")

    # Apply filters
    if search_query:
        employees = employees.filter(
            Q(SAP_ID__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
        )
    if employee_type:
        employees = employees.filter(employee_type__name=employee_type)
    if designation:
        employees = employees.filter(designation__title=designation)
    if employee_grade:
        employees = employees.filter(employee_grade__grade_name=employee_grade)
    if branch:
        employees = employees.filter(branch__branch_name__icontains=branch)
    if cadre:
        employees = employees.filter(cadre__name=cadre)
    if region:
        employees = employees.filter(region__name=region)

    # Ensure no duplicates
    employees = employees.distinct().order_by("SAP_ID")

    # Pagination
    paginator = Paginator(employees, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Check if it's an AJAX request
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = {
            "employees": [
                {
                    "SAP_ID": emp.SAP_ID,
                    "name": emp.name if emp.name else "N/A",
                    "employee_type": (
                        emp.employee_type.name if emp.employee_type else "N/A"
                    ),
                    "designation": emp.designation.title if emp.designation else "N/A",
                    "employee_grade": (
                        emp.employee_grade.grade_name if emp.employee_grade else "N/A"
                    ),
                    "branch": emp.branch.branch_name if emp.branch else "N/A",
                    "branch_code": emp.branch.branch_code if emp.branch else "N/A",
                    "region": emp.region.name if emp.region else "N/A",
                    "pending_inquiry": "Yes" if emp.pending_inquiry else "No",
                    "remarks": emp.remarks,
                    "transfer_remarks": emp.transfer_remarks,
                    "grade_assignment": emp.grade_assignment,
                }
                for emp in page_obj.object_list
            ],
            "total_count": paginator.count,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "next_page_number": (
                page_obj.next_page_number() if page_obj.has_next() else None
            ),
        }
        return JsonResponse(data)

    # Prepare context for template rendering
    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "employee_type": employee_type,
        "designation": designation,
        "employee_grade": employee_grade,
        "branch": branch,
        "cadre": cadre,
        "region": region,
        "employee_types": EmployeeType.objects.all(),
        "designations": Designation.objects.all(),
        "employee_grades": EmployeeGrade.objects.all(),
        "branches": Branch.objects.all(),
        "cadres": Cadre.objects.all(),
        "regions": Region.objects.all(),
    }

    return render(request, "employee_search/search.html", context)


@login_required(login_url="account:login")
@admin_or_admin_employee_required
def export_csv(request):
    # Get filter parameters (same as in advanced_search)
    search_query = request.GET.get("search", "")
    employee_type = request.GET.get("employee_type", "")
    designation = request.GET.get("designation", "")
    employee_grade = request.GET.get("employee_grade", "")
    branch = request.GET.get("branch", "")
    cadre = request.GET.get("cadre", "")
    region = request.GET.get("region", "")

    # Get visible columns from request
    visible_columns = request.GET.get("visible_columns", "")

    # Map frontend column names to backend column names
    column_name_mapping = {
        "sap-id": "SAP_ID",
        "name": "name",
        "email": "email",
        "type": "employee_type",
        "designation": "designation",
        "grade": "employee_grade",
        "branch": "branch",
        "cnic": "cnic",
        "father-name": "father_name",
        "cadre": "cadre",
        "qualifications": "qualifications",
        "region": "region",
        "retirement": "retirement",
        "posting": "posting",
        "birth-date": "birth_date",
        "contract-expiry": "contract_expiry",
        "current-posting": "current_posting",
        "mobile": "mobile",
        "branch-code": "branch_code",
        "pending-inquiry": "pending_inquiry",
        "remarks": "remarks",
        "transfer-remarks": "transfer_remarks",
        "grade-assignment": "grade_assignment",
    }

    if visible_columns:
        # Split the comma-separated string into a list
        frontend_columns = visible_columns.split(",")
        # Map frontend column names to backend column names
        visible_columns = [
            column_name_mapping.get(col, col) for col in frontend_columns
        ]
    else:
        # Default to all columns if none specified
        visible_columns = [
            "SAP_ID",
            "name",
            "email",
            "employee_type",
            "designation",
            "employee_grade",
            "branch",
            "branch_code",
            "region",
            "pending_inquiry",
            "remarks",
            "transfer_remarks",
            "grade_assignment",
        ]

    # Base queryset
    employees = Employee.objects.exclude(region__isnull=True, SAP_ID__isnull=True)
    if request.user.user_group:
        employees = employees.filter(user_group=request.user.user_group)

    # Apply filters
    if search_query:
        employees = employees.filter(
            Q(SAP_ID__icontains=search_query)
            | Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
        )
    if employee_type:
        employees = employees.filter(employee_type__name=employee_type)
    if designation:
        employees = employees.filter(designation__title=designation)
    if employee_grade:
        employees = employees.filter(employee_grade__grade_name=employee_grade)
    if branch:
        employees = employees.filter(branch__branch_name__icontains=branch)
    if cadre:
        employees = employees.filter(cadre__name=cadre)
    if region:
        employees = employees.filter(region__name=region)

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="employee_data.csv"'

    # Create CSV writer
    writer = csv.writer(response)

    # Define column mappings (display name to model field)
    column_mapping = {
        "SAP_ID": {"header": "SAP ID", "field": "SAP_ID"},
        "name": {"header": "Name", "field": "name"},
        "email": {"header": "Email", "field": "email"},
        "employee_type": {"header": "Employee Type", "field": "employee_type__name"},
        "designation": {"header": "Designation", "field": "designation__title"},
        "employee_grade": {
            "header": "Employee Grade",
            "field": "employee_grade__grade_name",
        },
        "branch": {"header": "Branch", "field": "branch__branch_name"},
        "branch_code": {"header": "Branch Code", "field": "branch__branch_code"},
        "region": {"header": "Region", "field": "region__name"},
        "pending_inquiry": {"header": "Pending Inquiry", "field": "pending_inquiry"},
        "remarks": {"header": "Remarks", "field": "remarks"},
        "transfer_remarks": {"header": "Transfer Remarks", "field": "transfer_remarks"},
        "grade_assignment": {"header": "Grade Assignment", "field": "grade_assignment"},
        "cnic": {"header": "CNIC", "field": "cnic_no"},
        "father_name": {
            "header": "Father/Husband Name",
            "field": "husband_or_father_name",
        },
        "cadre": {"header": "Cadre", "field": "cadre__name"},
        "qualifications": {"header": "Qualifications", "field": "qualifications"},
        "retirement": {"header": "Retirement Date", "field": "date_of_retirement"},
        "posting": {"header": "Place of Posting", "field": "place_of_posting"},
        "birth_date": {"header": "Birth Date", "field": "birth_date"},
        "contract_expiry": {
            "header": "Contract Expiry",
            "field": "date_of_contract_expiry",
        },
        "current_posting": {
            "header": "Current Posting Date",
            "field": "date_current_posting",
        },
        "mobile": {"header": "Mobile Number", "field": "mobile_number"},
    }

    # Write header row with only visible columns
    header_row = [
        column_mapping[col]["header"]
        for col in visible_columns
        if col in column_mapping
    ]
    writer.writerow(header_row)

    # Write data rows
    for employee in employees:
        row = []
        for col in visible_columns:
            if col in column_mapping:
                field = column_mapping[col]["field"]
                # Handle foreign key relationships
                if (
                    field.endswith("__name")
                    or field.endswith("__title")
                    or field.endswith("__grade_name")
                    or field.endswith("__branch_code")
                    or field.endswith("__branch_name")
                ):
                    parts = field.split("__")
                    base_field = parts[0]
                    attr = parts[1]
                    related_obj = getattr(employee, base_field)
                    value = getattr(related_obj, attr) if related_obj else ""
                elif field == "pending_inquiry":
                    value = "Yes" if getattr(employee, field) else "No"
                elif field == "qualifications":
                    # Handle ManyToMany relationship for qualifications
                    qualifications = employee.qualifications.all()
                    value = (
                        ", ".join([q.name for q in qualifications])
                        if qualifications
                        else ""
                    )
                else:
                    value = getattr(employee, field, "")
                row.append(value)
        writer.writerow(row)

    return response


@login_required(login_url="account:login")
@admin_or_admin_employee_required
def get_branches_by_region(request):
    """Get branches for a specific region"""
    region_name = request.GET.get("region", "")

    if region_name:
        # Filter branches by the selected region
        branches = Branch.objects.filter(region__name=region_name).order_by(
            "branch_name"
        )
    else:
        # If no region is selected, return all branches
        branches = Branch.objects.all().order_by("branch_name")

    # Format the response data
    data = {
        "branches": [
            {
                "id": branch.id,
                "branch_name": branch.branch_name,
                "branch_code": branch.branch_code,
            }
            for branch in branches
        ]
    }

    return JsonResponse(data)
