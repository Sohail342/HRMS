from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import DetailView, ListView
from HRIS_App.models import Employee
from django.views.generic import ListView


#  AJAX request
def get_employee_data(request):
    sap_id = request.GET.get('sap_id')
    employee = get_object_or_404(Employee, SAP_ID=sap_id, admin_signuture=True)

    
    data = {
        'full_name': employee.full_name,
        'designation': str(employee.designation),
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
        context['admin_signuture'] = Employee.objects.filter(admin_signuture=True)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        return context
    

class LeaveMemorandum(MemorandumMixin, DetailView):
    template_name = 'reporting/letter_templates/leave_memorandum.html' 
    

class GrantOfExtensionMemorandum(MemorandumMixin, DetailView):
    template_name = 'reporting/letter_templates/grant_of_extension.html'


class JoiningMemorandum(MemorandumMixin, DetailView):
    template_name = 'reporting/letter_templates/joining_memorandun.html'

class ApprovalPermissionHospitilization(MemorandumMixin, DetailView):
    template_name = 'reporting/letter_templates/approval_permission_hospitalization.html'


class MaternityLeaveMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/maternity_Leave.html' 


class RequestForIssuanceOfficeMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/request_for_issuance.html' 


class OrderOfficeMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/order_office_memorandum.html'   


class PaymentOfBillMemorandum(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/payment_of_bill.html'  


class ReimbursementMemorandum(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/reimbursement.html' 


class PermissionOfHospitalization(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/permission_of_hospitalization.html'  

class ReimbursementAgainstPurchase(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/reimbursement_against_purchase.html' 


class RelievingOrderMemorandum(MemorandumMixin, DetailView): 
  template_name = 'reporting/letter_templates/relieving_order.html'



class LetterForm(ListView):
    model = Employee
    context_object_name = 'employees'
    template_name = 'reporting/letter_form.html'
    
    FORM_TYPE_MAPPING = {
        'leave_memorandum': 'reporting:leave_memorandum',
        'joining_memorandum': 'reporting:joining_memorandum',
        'order_office_memorandun': 'reporting:order_office_memorandun',
        'approval_permission_hospitalization': 'reporting:approval_permission_hospitalization',
        'maternity_Leave': 'reporting:maternity_Leave',
        'request_for_issuance': 'reporting:request_for_issuance',
        'payment_of_bill': 'reporting:payment_of_bill',
        'grant_of_extension': 'reporting:grant_of_extension',
        'reimbursement': 'reporting:reimbursement',
        'permission_of_hospitalization': 'reporting:permission_of_hospitalization',
        'reimbursement_against_purchase': 'reporting:reimbursement_against_purchase',
        'relieving_order': 'reporting:relieving_order',
    }

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')
        sap_id = request.POST.get('sap_id')
        
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


    
