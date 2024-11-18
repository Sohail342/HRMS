from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
import csv
from django.db.models.functions import Length, Cast
from django.db.models import CharField
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import (
    Designation, 
    Employee, 
    EmployeeType, 
    Cadre, 
    EmployeeGrade, 
    Branch, 
    Qualification,
)

def employees_view(request):
    employees = Employee.objects.all().order_by('SAP_ID')
    search_query = request.GET.get('search', '')
    employee_type = request.GET.get('employee_type', '')
    designation = request.GET.get('designation', '')
    cadre = request.GET.get('cadre', '')
    employee_grade = request.GET.get('employeeGrade', '')
    branch = request.GET.get('branch', '')
    qualification = request.GET.get('qualification', '')

    # Apply filters
    if branch:
        employees = employees.filter(branch__branch_name__icontains=branch)
    if qualification:
        employees = employees.filter(qualifications__name__icontains=qualification)
    if search_query:
        employees = employees.filter(SAP_ID__icontains=search_query)
    if employee_type:
        employees = employees.filter(employee_type=employee_type)
    if cadre:
        employees = employees.filter(cadre__name=cadre)
    if designation:
        employees = employees.filter(designation__title=designation)
    if employee_grade:
        employees = employees.filter(employee_grade__grade_name=employee_grade)

    # Ensure no duplicates if using M2M relationships
    employees = employees.distinct()  

    # Pagination
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check if it's an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            'employees': [
                {
                    'SAP_ID': emp.SAP_ID,
                    'cnic_no': emp.cnic_no,
                    'full_name': emp.full_name,
                    'husband_or_father_name': emp.husband_or_father_name,
                    'employee_type': emp.employee_type.name if emp.employee_type else "N/A",
                    'designation': emp.designation.title if emp.designation else "N/A",
                    'cadre': emp.cadre.name if emp.cadre else "N/A",
                    'employee_grade': emp.employee_grade.grade_name if emp.employee_grade else "N/A",
                    'branch': emp.branch.branch_name if emp.branch else "N/A",
                    'qualifications': [qual.name for qual in emp.qualifications.all()],
                    'mobile_no': emp.mobile_no,
                    'phone_no_official': emp.phone_no_official,
                    'phone_no_emergency_contact': emp.phone_no_emergency_contact,
                    'employee_email': emp.employee_email,
                    'date_of_last_promotion': emp.date_of_last_promotion,
                    'date_current_posting': emp.date_current_posting,
                    'date_current_assignment': emp.date_current_assignment,
                    'date_of_retirement': emp.date_of_retirement,
                }
                for emp in page_obj.object_list
            ],
            'total_count': paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        }
        return JsonResponse(data)

    # Prepare context for rendering
    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "employee_type": employee_type,
        "designation": designation,
        "employee_types": EmployeeType.objects.all(),
        "designations": Designation.objects.all(),
        'cadre': Cadre.objects.all(),
        'employeeGrade': EmployeeGrade.objects.all(),
        'branches': Branch.objects.all(),
        'qualifications': Qualification.objects.all(),
    }

    return render(request, 'core/employee.html', context)







def download_employees_csv(request):
    # Get all employee data
    
    employee_type = request.GET.get('employee_type', None)
    designation = request.GET.get('designation', None)
    cadre = request.GET.get('cadre', None)
    employee_grade = request.GET.get('employeeGrade', None)
    branch = request.GET.get('branch', None)
    qualification = request.GET.get('qualification', None)
    search_query = request.GET.get('search', None)
 
    employees = Employee.objects.all().order_by('SAP_ID')

    # Apply filters
    if branch:
        employees = employees.filter(branch__branch_name__icontains=branch)
    if qualification:
        employees = employees.filter(qualifications__name__icontains=qualification)
    if search_query:
        employees = employees.filter(SAP_ID__icontains=search_query)
    if employee_type:
        employees = employees.filter(employee_type=employee_type)
    if cadre:
        employees = employees.filter(cadre__name=cadre)
    if designation:
        employees = employees.filter(designation__title=designation)
    if employee_grade:
        employees = employees.filter(employee_grade__grade_name=employee_grade)

    # Ensure no duplicates if using M2M relationships
    employees = employees.distinct()  

    # Get the selected columns from the request
    selected_columns = request.GET.get('columns', '').split(',')
    
    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response)
    
    # Define a mapping of column names to the employee model fields
    column_mapping = {
        'SAP ID': 'SAP_ID',
        'CNIC No': 'cnic_no',
        'Full Name': 'full_name',
        'F.Name': 'husband_or_father_name',
        'Employee Type': 'employee_type',
        'Designation': 'designation',
        'Cadre': 'cadre',
        'Employee Grade': 'employee_grade',
        'Branch': 'branch',
        'Qualifications': 'qualifications',
        'Mobile No': 'mobile_no',
        'Official Phone No': 'phone_no_official',
        'Emergency Contact No': 'phone_no_emergency_contact',
        'Email': 'employee_email',
        'Last Promotion Date': 'date_of_last_promotion',
        'Current Posting Date': 'date_current_posting',
        'Current Assignment Date': 'date_current_assignment',
        'Retirement Date': 'date_of_retirement',
    }

    # Write header row with only selected columns
    writer.writerow(selected_columns)

    # Write data rows for each selected column
    for employee in employees:
        row = []
        for col in selected_columns:
            if col in column_mapping:
                row.append(getattr(employee, column_mapping[col], ''))
        writer.writerow(row)
    

    return response




def index(request):
    # employees = Employee.objects.count()
    # new_employees = Employee.objects.annotate(sap_id_length=Length(Cast('SAP_ID', output_field=CharField()))).filter(sap_id_length__gt=5).count()

    context = {
        'new_employees':"new_employees",
        'employees':"employees"
    }
    
    return render(request, 'index.html', context)




def employee_detail_view(request, sap_id):
    employee = get_object_or_404(Employee, SAP_ID=sap_id)
    return render(request, 'core/employee_details.html', {'employee': employee})
