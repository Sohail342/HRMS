from django.views.generic import UpdateView
from .forms import InquiryPendingForm, TransferForm
from HRIS_App.models import Employee
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import Inquiry


class InquiryPending(UpdateView):
    model = Employee
    form_class = InquiryPendingForm
    template_name = 'transfer_employees/inquiry.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Employee, SAP_ID=self.kwargs['SAP_ID'])
    
    def get_success_url(self):
        # Return the URL as a string using reverse
        return reverse('HRMS:employees_view')

    def form_valid(self, form):
        # Save the form and redirect to the success URL
        response = super().form_valid(form)

        return redirect(self.get_success_url())
    

class TransferView(UpdateView):
    model = Employee
    form_class = TransferForm
    template_name = 'transfer_employees/transfer_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Employee, SAP_ID=self.kwargs['SAP_ID'])
    
    def get_success_url(self):
        # Return the URL as a string using reverse
        return reverse('HRMS:employees_view')

    def form_valid(self, form):
        # Save the form and redirect to the success URL
        response = super().form_valid(form)

        # Create and save an inquiry record after the form is valid
        Inquiry.objects.create(
            admin_employee=self.object,
            transfer_remarks=form.cleaned_data['transfer_remarks'],
            transferred_status=form.cleaned_data['transferred_status'],
            transferred_employee = self.kwargs['SAP_ID']
        )
        return redirect(self.get_success_url())
    


