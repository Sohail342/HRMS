from django import forms
from .models import ContractRenewal
from .models import EducationalDocument , NonInvolvementCertificate, StationaryRequest
from .models_leave_management import EmployeeLeaveApplication
from HRIS_App.custom_forms import RequiredOptionalFieldsModelForm

class ContractRenewalForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = ContractRenewal
        fields = ['position', 'contract_expiry_date', 'reason', 'renewal_document']



class EducationalDocumentForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = EducationalDocument
        fields = ['document_type', 'document']
        widgets = {
            'document_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter document type (e.g., Degree)'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }
        

class NonInvolvementCertificateForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = NonInvolvementCertificate
        fields = ['request_date', 'reason', 'supporting_docs']
        widgets = {
            'request_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
        
class StationaryRequestForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = StationaryRequest
        fields = ['item_name', 'quantity', 'reason_for_request', 'request_date']
        widgets = {
            'request_date': forms.DateInput(attrs={'type': 'date'}),
        }


#----------------------------- Leave Management -------------------------------------------

class PermanentLeaveApplicationForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = EmployeeLeaveApplication
        fields = ['from_date', 'to_date', 'reason', 'leave_type', 'supervisor_signature']

        widgets = {
            'leave_date': forms.DateInput(attrs={'type': 'date'}),
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        if from_date and to_date:
            if from_date > to_date:
                raise forms.ValidationError("From Date cannot be later than To Date.")
        return cleaned_data


class PermanentLeaveApplicationForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = EmployeeLeaveApplication
        fields = ['leave_type', 'from_date', 'to_date', 'reason', 'supervisor_signature']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
        