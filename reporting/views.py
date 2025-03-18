from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils import timezone
from group_head.decorators import admin_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
import cloudinary
from .models import Signature, LetterTemplates
from django.views.generic import DetailView, ListView
from HRIS_App.models import Employee
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView



def get_employee(request):
    sap_id = request.GET.get('sap_id')
    employee = get_object_or_404(Employee, SAP_ID=sap_id)

    data = {
        'employee_name': employee.name,
        'designation': employee.designation_id,
        'sap_id': str(employee.SAP_ID) if employee.SAP_ID else "", 
        'employee_grade': str(employee.employee_grade)
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
    
@method_decorator(admin_required, name='dispatch')
class LeaveMemorandum(MemorandumMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        context['admin_signuture'] = Signature.objects.all()
        return context
    template_name = 'reporting/letter_templates/leave_memorandum.html' 

    
@method_decorator(admin_required, name='dispatch')
class GrantOfExtensionMemorandum(MemorandumMixin, DetailView):
    template_name = 'reporting/letter_templates/grant_of_extension.html'


@method_decorator(admin_required, name='dispatch')
class JoiningMemorandum(MemorandumMixin, DetailView):
    template_name = 'reporting/letter_templates/joining_memorandun.html'


@method_decorator(admin_required, name='dispatch')
class Hospitilization(MemorandumMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()

        employee_type = str(context['employee'].employee_type)
        context['employee_type'] = employee_type
        return context
    template_name = 'reporting/letter_templates/hospitalization.html'


@method_decorator(admin_required, name='dispatch')
class MaternityLeaveMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/maternity_Leave.html' 


@method_decorator(admin_required, name='dispatch')
class RequestForIssuanceOfficeMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/request_for_issuance.html' 


@method_decorator(admin_required, name='dispatch')
class OrderOfficeMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/order_office_memorandum.html'   


@method_decorator(admin_required, name='dispatch')
class PaymentOfBillMemorandum(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/payment_of_bill.html'  


@method_decorator(admin_required, name='dispatch')
class ReimbursementMemorandum(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/reimbursement.html' 



@method_decorator(admin_required, name='dispatch')
class ReimbursementAgainstPurchase(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/reimbursement_against_purchase.html' 


@method_decorator(admin_required, name='dispatch')
class RelievingOrderMemorandum(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/relieving_order.html'



@method_decorator(admin_required, name='dispatch')
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
                    uploaded_file, resource_type="raw", format="pdf", folder="BSC Forms"
                )
                template_url = upload_result['secure_url']

                # Save template record
                template_upload = LetterTemplates(employee=employee, template_url=template_url)
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
    







    
