from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils import timezone
from group_head.decorators import is_letter_template_admin_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
import cloudinary
import json
import base64
from datetime import datetime
from .models import Signature, LetterTemplates, HospitalName, PermenantLetterTemplates
from django.views.generic import DetailView, ListView
from HRIS_App.models import Employee
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from employee_attendance.models import LeaveApplication


@csrf_exempt
def save_pdf_to_cloudinary(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pdf_data = data.get('pdf_data')
            sap_id = data.get('sap_id')
            
            # Validate the data
            if not pdf_data or not sap_id:
                return JsonResponse({'success': False, 'error': 'Missing required data'}, status=400)
            
            # Get the employee object
            employee = get_object_or_404(Employee, SAP_ID=sap_id)
            
            # Convert base64 to file
            pdf_data = pdf_data.split(',')[1] if ',' in pdf_data else pdf_data
            pdf_bytes = base64.b64decode(pdf_data)
            
            # Upload PDF to Cloudinary
            upload_result = cloudinary.uploader.upload(
                pdf_bytes, 
                resource_type="raw", 
            )
            
            template_url = upload_result['secure_url']
            
            # Save template record
            template_upload = LetterTemplates(employee=employee, template_saved_url=template_url)
            template_upload.save()
            
            return JsonResponse({'success': True, 'url': template_url})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def get_employee(request):
    sap_id = request.GET.get('sap_id')
    employee = get_object_or_404(Employee, SAP_ID=sap_id)

    data = {
        'employee_name': employee.name,
        'designation': employee.designation_id,
        'sap_id': str(employee.SAP_ID) if employee.SAP_ID else "", 
        'employee_grade': str(employee.employee_grade),
        'employee_salutation': str(employee.employee_salutation),
    }
    return JsonResponse(data)



#  AJAX request
def get_employee_data(request):
    sap_id = request.GET.get('sap_id')
    employee = get_object_or_404(Signature, SAP_ID=sap_id)

    
    data = {
        'employee_name': employee.employee_name if employee.employee_name else "",
        'designation': str(employee.designation) if employee.designation else "",
        'grade': str(employee.grade) if employee.grade else "",
        'department': str(employee.department) if employee.department else "",
        'wing': str(employee.wing) if employee.wing else "",
        'division': str(employee.division) if employee.division else "",
        'group': str(employee.group) if employee.group else "", 
    }

    return JsonResponse(data)



class MemorandumMixin:
    model = Employee
    context_object_name = 'employee'
    
    def get_object(self):
        sap_id = self.kwargs.get('sap_id')
        return get_object_or_404(Employee, SAP_ID=sap_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        return context
    
@method_decorator(is_letter_template_admin_required, name='dispatch')
class LeaveMemorandum(MemorandumMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        context['admin_signuture'] = Signature.objects.all()
        context['hospital_name'] = HospitalName.objects.all()
        return context
    template_name = 'reporting/letter_templates/leave_memorandum.html' 


@method_decorator(is_letter_template_admin_required, name='dispatch')
class Hospitilization(MemorandumMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        context['admin_signuture'] = Signature.objects.all()
        context['hospital_name'] = HospitalName.objects.all()

        employee_type = str(context['employee'].employee_type)
        context['employee_type'] = employee_type
        return context
    template_name = 'reporting/letter_templates/hospitalization.html'



@method_decorator(is_letter_template_admin_required, name='dispatch')
class RequestForIssuanceOfficeMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/request_for_issuance.html' 




@is_letter_template_admin_required
def template_search(request):
    search_performed = False
    templates = None
    
    if 'sap_id' in request.GET and request.GET['sap_id']:
        search_performed = True
        sap_id = request.GET['sap_id']
        
        # Get the employee object
        try:
            employee = Employee.objects.get(SAP_ID=sap_id)
            # Get all templates for this employee
            template_list = LetterTemplates.objects.filter(employee=employee).order_by('-created_at')
            
            # Pagination
            paginator = Paginator(template_list, 10)
            page = request.GET.get('page', 1)
            templates = paginator.get_page(page)
            
        except Employee.DoesNotExist:
            # No employee found with this SAP ID
            templates = []
    
    context = {
        'templates': templates,
        'search_performed': search_performed
    }
    
    return render(request, 'reporting/template_search.html', context)



@is_letter_template_admin_required
def search_permanent_saved_templates(request):
    search_performed = False
    templates = None
    
    if 'sap_id' in request.GET and request.GET['sap_id']:
        search_performed = True
        sap_id = request.GET['sap_id']
        
        # Get the employee object
        try:
            employee = Employee.objects.get(SAP_ID=sap_id)
            # Get all templates for this employee
            template_list = PermenantLetterTemplates.objects.filter(employee=employee).order_by('-created_at')
            
            # Pagination
            paginator = Paginator(template_list, 10)
            page = request.GET.get('page', 1)
            templates = paginator.get_page(page)
            
        except Employee.DoesNotExist:
            # No employee found with this SAP ID
            templates = []
    
    context = {
        'templates': templates,
        'search_performed': search_performed
    }
    
    return render(request, 'reporting/search_permanant.html', context)



class LetterForm(LoginRequiredMixin, ListView):
    
    model = Employee
    context_object_name = 'employees'
    template_name = 'reporting/letter_form.html'
    login_url = 'account:login'
    
    FORM_TYPE_MAPPING = {
        'leave_memorandum': 'reporting:leave_memorandum',
        'joining_memorandum': 'reporting:joining_memorandum',
        'order_office_memorandun': 'reporting:order_office_memorandun',
        'hospitalization': 'reporting:hospitalization',
        'maternity_Leave': 'reporting:maternity_Leave',
        'request_for_issuance': 'reporting:request_for_issuance',
        'payment_of_bill': 'reporting:payment_of_bill',
        'grant_of_extension': 'reporting:grant_of_extension',
        'reimbursement': 'reporting:reimbursement',
        'reimbursement_against_purchase': 'reporting:reimbursement_against_purchase',
        'relieving_order': 'reporting:relieving_order',
    }



    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')
        sap_id = request.POST.get('sap_id')
        description = request.POST.get('description')
        sap_id_for_template_upload = request.POST.get('sap_id_for_template_upload')

        if 'pdf_file' in request.FILES:
            uploaded_file = request.FILES['pdf_file']

            # Validate the file type (only allow PDF)
            if not uploaded_file.name.endswith('.pdf'):
                messages.error(request, "Only PDF files are allowed.")
                return redirect('reporting:lettername')

            # Get the employee object
            employee = get_object_or_404(Employee, SAP_ID=sap_id_for_template_upload)

            try:
                # Upload PDF to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    uploaded_file, resource_type="raw"
                )   
                template_url = upload_result['secure_url']

                # Save template record
                template_upload = PermenantLetterTemplates(employee=employee, template_saved_url=template_url, description=description)
                template_upload.save()

                messages.success(request, "Template uploaded successfully.")
                return redirect('reporting:lettername')

            except ValidationError as e:
                messages.error(request, f"Error uploading file: {e}")

                return redirect('reporting:lettername')

        
        # Validate SAP ID
        try:
            verify_sap_id = Employee.objects.get(SAP_ID=sap_id)
        except Employee.DoesNotExist:
            errors = "SAP ID is not registered."
            return render(request, self.template_name, {'errors': errors, 'employees': self.get_queryset()})
        
        # Redirect based on the form type
        redirect_view = self.FORM_TYPE_MAPPING.get(form_type)
        if redirect_view:
            return redirect(redirect_view, sap_id=sap_id)
        
        # If no valid form type, render the same page with error
        errors = "Invalid form type."
        return render(request, self.template_name, {'errors': errors, 'employees': self.get_queryset()})



@is_letter_template_admin_required
def application_leave(request, sap_id):
    if request.method == 'POST':

        leave_type = request.POST.get('leave_type_option')
        leave_days = request.POST.get('granted_leaves') 
        from_date_str = request.POST.get('effect_from')
        reason = request.POST.get('purpose')

        # Convert string date to datetime object first
        date_format = "%Y-%m-%d"
        from_date = datetime.strptime(from_date_str, date_format).date()
        
        # Calculate to_date using the datetime object
        to_date = from_date + timezone.timedelta(days=(int(leave_days) - 1) + 1 )

        # Calculate availed leave
        availed_leave = (to_date - from_date).days + 1
        
        # Convert Leave type to Full form
        if leave_type == 'CL':
            leave_type = 'Casual'
        elif leave_type == 'ML':
            leave_type = 'Mandatory'
        elif leave_type == 'SL':
            leave_type = 'Sick'
        elif leave_type == 'PL':
            leave_type = 'Privilege'
        elif leave_type == 'Ex-Pak':
            leave_type = 'Ex-Pakistan'


        # Validate the data
        if not sap_id or not leave_type or not from_date or not reason:
            messages.error(request, "All fields are required.")
            return redirect('reporting:leave_memorandum', sap_id=sap_id)

        # Get the employee object
        employee = get_object_or_404(Employee, SAP_ID=sap_id)

        # Save the leave application
        leave_application = LeaveApplication(
            employee=employee,
            application_type=leave_type,
            leave_date=datetime.now().date(),
            from_date=from_date,
            to_date=to_date,
            reason=reason,
            availed_leaves=int(leave_days)
        )
        leave_application.save()

        messages.success(request, "Leave application submitted successfully.")
        return redirect('reporting:leave_memorandum', sap_id=sap_id)

    return render(request, 'reporting/leave_memorandum.html', sap_id=sap_id)
    







    
