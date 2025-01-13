from HRIS_App.models import Employee, Region
from django.shortcuts import render, redirect
import json
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.views import View
from django.contrib import messages
import cloudinary
from .decorators import admin_required
from django.contrib.auth.decorators import login_required
from HRIS_App.calculate_remaining_grades import calculate_remaining_grades
from django.core.paginator import Paginator
from django.http import JsonResponse
from HRIS_App.models import (
    Designation, 
    Employee, 
    EmployeeType, 
    Cadre, 
    EmployeeGrade, 
    Branch, 
    Qualification,
)

# Assigned grades of all regions
@admin_required
def grade_distribution_view(request):
    GRADE_CHOICES = [
        'Excellent',
        'Very Good',
        'Good',
        'Needs Improvement',
        'Unsatisfactory',
        'Not Assigned',
    ]

    regions = Employee.objects.values_list('region__name', flat=True).distinct()

    grade_data = []
    totals = {grade: 0 for grade in GRADE_CHOICES}
    totals['total_employees'] = 0

    for region in regions:
        branch_data = {'branch': region, 'total_employees': 0}

        for grade in GRADE_CHOICES:
            if grade == "Not Assigned":
                count = Employee.objects.filter(region__name=region, grade_assignment="Not Assigned", is_admin=False).count()
            else:
                count = Employee.objects.filter(region__name=region, grade_assignment=grade, is_admin=False).count()

            branch_data[grade] = count
            totals[grade] += count  # Add to totals for this grade

        branch_data['total_employees'] = Employee.objects.filter(region__name=region, is_admin=False).count()
        totals['total_employees'] += branch_data['total_employees'] 

        grade_data.append(branch_data)

    context = {
        'grade_data': grade_data,
        'grades': GRADE_CHOICES,
        'totals': totals,
    }
    return render(request, 'group_head/grade_distribution.html', context)



# Assigned Grades of each region
@admin_required
@login_required(login_url='account:login')
def grade_distribution_region_view(request, region_name):
    employees = Employee.objects.filter(region=region_name).order_by('SAP_ID')
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

    # Calcute grades
    remaining_grades = calculate_remaining_grades(region=region_name)

    # Pagination
    paginator = Paginator(employees, 50)
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
        'region_name':region_name,
        "search_query": search_query,
        "employee_type": employee_type,
        "designation": designation,
        "employee_types": EmployeeType.objects.all(),
        "designations": Designation.objects.all(),
        'cadre': Cadre.objects.all(),
        'employeeGrade': EmployeeGrade.objects.all(),
        'branches': Branch.objects.filter(region=region_name),
        'qualifications': Qualification.objects.all(),
        'remaining_grades': remaining_grades,
    }

    return render(request, 'group_head/grade_distribution_branch.html', context)



# Ajax for update or assign grades for all regions by Group Head
@login_required(login_url='account:login')
@admin_required
def assign_grade(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            employee_id = data.get('employee_id')
            grade_assignment = data.get('grade_assignment')

            # Fetch the employee
            employee = Employee.objects.get(SAP_ID=employee_id)
            employee.grade_assignment = grade_assignment
            employee.save()

            return JsonResponse({"success": True, "message": "Grade updated successfully."})
        except Employee.DoesNotExist:
            return JsonResponse({"success": False, "message": "Employee not found."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)



# Upload Assigned Grades By Branches on Cloudinary
@admin_required
def AssignedGradesByBranchesView(request, region_id):

    # Ensure the region exists or create a new region
    region, created = Region.objects.get_or_create(region_id=region_id)

    if request.method == 'POST':
        csv_file = request.FILES.get('file')

        if csv_file:
            try:
                # Upload CSV to Cloudinary
                upload_result = cloudinary.uploader.upload(csv_file,  resource_type = "raw") 

                # Store the URL of the uploaded file in the model
                region.csv_file = upload_result['secure_url']
                region.save()

                messages.success(request, "CSV file uploaded successfully!")
                return redirect("group_head:upload_Assigned_grades", region_id=region_id)

            except Exception as e:
                messages.error(request, e)
                return redirect("group_head:upload_Assigned_grades", region_id=region_id)

    return render(request, 'group_head/AssignedGradesByBranches.html', {"region":region})



# Uploaded CSV files
@admin_required
def uploaded_csv_files(request):
    regions_csv_files = Region.objects.values('region_id', 'name', 'csv_file')

   # Append '.csv' to each CSV file URL if not already present
    for region in regions_csv_files:

        if region['csv_file']:
            csv_url = str(region['csv_file'])
            
            # Check if the URL ends with '.csv' and append if not
            if not csv_url.endswith('.csv'):
                region['csv_file'] = f"{csv_url}.csv"
        
    uploaded_data = {
        'regions_csv_files':regions_csv_files,
    }
    return render(request, 'group_head/uploaded_files.html', uploaded_data)



# Search for employee
@method_decorator(admin_required, name='dispatch')
class SearchEmployee(View):
    def get(self, request):
        query = request.GET.get('search', '')
        employee_pdf_files = []
        employee = None
        url = None

        try:
            employee = Employee.objects.get(SAP_ID__icontains=query) if query else None

            if query:
                employee_pdf_files = Employee.objects.filter(SAP_ID__icontains=query).values('name', 'pdf_file')

        except Employee.DoesNotExist:
            messages.error(request, 'No employees found matching your search.')
            

    # Append '.pdf' to each pdf file URL if not already present
        for pdf in employee_pdf_files:
            if pdf['pdf_file']:
                pdf_url = str(pdf['pdf_file'])
                
                # Check if the URL ends with '.csv' and append if not
                if not pdf_url.endswith('.pdf'):
                    pdf['pdf_file'] = f"{pdf_url}.pdf"
                    url = pdf['pdf_file']
                    print(url)
            

        context = {
        'employee_pdf_file':url,
        'employee':employee,
        'query':query,
         }
        
        return render(request, 'group_head/search_employee.html', context)
    



# Upload PDF (BSC Form for employees on Cloudinary)
@method_decorator(admin_required, name='dispatch')
class UploadBSCFrom(View):
    def get(self, request, *args, **kwargs):
        # Render the upload form
        employee = Employee.objects.get(SAP_ID=kwargs['sap_id'])

        return render(request, 'group_head/upload_employee_pdf.html', {"employee":employee})

    def post(self, request, *args, **kwargs):
        employee = Employee.objects.get(SAP_ID=kwargs['sap_id'])

        if 'pdf_file' in request.FILES:
            uploaded_file = request.FILES['pdf_file']

            # Validate the file type (only allow PDF)
            if not uploaded_file.name.endswith('.pdf'):
                messages.error(request, "Only PDF files are allowed.")
                return redirect('group_head:upload_pdf', sap_id=employee.SAP_ID)

            # Save the file to Cloudinary
            try:
                # Upload PDF to Cloudinary
                upload_result = cloudinary.uploader.upload(uploaded_file,  resource_type = "raw", format="pdf", folder="BSC Forms") 
                employee.pdf_file = upload_result['secure_url']
                employee.save() 

                messages.success(request, "PDF uploaded successfully.")
                return redirect('group_head:upload_pdf', sap_id=employee.SAP_ID)

            except ValidationError as e:
                messages.error(request, f"Error uploading file: {e}")
                return redirect('group_head:upload_pdf', sap_id=employee.SAP_ID)

        else:
            messages.error(request, "No PDF file uploaded.")
            return redirect('group_head:upload_pdf', sap_id=employee.SAP_ID)
