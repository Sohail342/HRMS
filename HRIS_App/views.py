from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
import csv
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import UpdateView
from .forms import AssignGradeForm
from django.db.models import CharField
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models.functions import Length, Cast
from .models import (
    Designation, 
    Employee, 
    EmployeeType, 
    Cadre, 
    EmployeeGrade, 
    Branch, 
    Qualification,
)




@login_required(login_url='account:login')
def employees_view(request):
    user_region = request.user.region   
    user_group = request.user.user_group
    employees = Employee.objects.filter(region=user_region, user_group=user_group).order_by('SAP_ID')
    search_query = request.GET.get('search', '')
    employee_type = request.GET.get('employee_type', '')
    designation = request.GET.get('designation', '')
    employee_grade = request.GET.get('employeeGrade', '')
    branch = request.GET.get('branch', '')

    # Apply filters
    if branch:
        employees = employees.filter(branch__branch_name__icontains=branch)
    if search_query:
        employees = employees.filter(SAP_ID__icontains=search_query)
    if employee_type:
        employees = employees.filter(employee_type=employee_type)
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
                    'name': emp.name if emp.name else "N/A",
                    'employee_type': emp.employee_type.name if emp.employee_type else "N/A",
                    'designation': emp.designation.title if emp.designation else "N/A",
                    'employee_grade': emp.employee_grade.grade_name if emp.employee_grade else "N/A",
                    'branch': emp.branch.branch_name if emp.branch else "N/A",
                    'Branch_code':emp.branch.branch_code if emp.branch else "N/A",
                    'date_of_joining': emp.date_of_joining,
                    'pending_inquiry': 'Yes' if emp.pending_inquiry else "No",
                    'remarks':emp.remarks,
                    'transfer_remarks':emp.transfer_remarks,
                    'grade_assignment':emp.grade_assignment,
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

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "employee_type": employee_type,
        "designation": designation,
        "employee_types": EmployeeType.objects.all(),
        "designations": Designation.objects.all(),
        'cadre': Cadre.objects.all(),
        'employeeGrade': EmployeeGrade.objects.all(),
        'branches': Branch.objects.filter(region=user_region),
        'qualifications': Qualification.objects.all(),
    }

    return render(request, 'HRIS_App/employee.html', context)







def download_employees_csv(request):
    # Get all employee data
    employee_region = request.user.region
    employee_type = request.GET.get('employee_type', None)
    designation = request.GET.get('designation', None)
    employee_grade = request.GET.get('employeeGrade', None)
    branch = request.GET.get('branch', None)
    search_query = request.GET.get('search', None)
 
    employees = Employee.objects.all().order_by('SAP_ID')

    # Apply filters
    if branch:
        employees = employees.filter(branch__branch_name__icontains=branch)

    if search_query:
        employees = employees.filter(SAP_ID__icontains=search_query)
    if employee_type:
        employees = employees.filter(employee_type=employee_type)
    if designation:
        employees = employees.filter(designation__title=designation)
    if employee_grade:
        employees = employees.filter(employee_grade__grade_name=employee_grade)
    if employee_region:
        employees = employees.filter(region__name=employee_region)

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
        'Full Name': 'name',
        'Employee Type': 'employee_type',
        'Designation': 'designation',
        'Employee Grade': 'employee_grade',
        'Branch': 'branch',
        'Joining Date': 'date_of_joining',
        'Pending Inquiry':'pending_inquiry',
        'Remarks':'remarks',
        'Transfer Remarks':'transfer_remarks',
        'APA 2024':"grade_assignment",
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
    employees = Employee.objects.count()
    new_employees = Employee.objects.annotate(sap_id_length=Length(Cast('SAP_ID', output_field=CharField()))).filter(sap_id_length__gt=5).count()

    context = {
        'new_employees':new_employees,
        'employees':employees
    }
    return render(request, 'index.html', context)



@login_required(login_url='account:login')
def employee_detail_view(request, sap_id):
    employee = get_object_or_404(Employee, SAP_ID=sap_id)
    return render(request, 'HRIS_App/employee_details.html', {'employee': employee})



class AssignGradeView(UpdateView):
    model = Employee
    form_class = AssignGradeForm
    template_name = 'HRIS_App/assign_grade.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Employee, SAP_ID=self.kwargs['sap_id'])
    
    def get_success_url(self):
        # Return the URL as a string using reverse
        return reverse('HRMS:employees_view')

    def form_valid(self, form):
        # Save the form and redirect to the success URL
        response = super().form_valid(form)

        return redirect(self.get_success_url())
