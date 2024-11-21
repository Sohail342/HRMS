from django import forms
from HRIS_App.models import Employee
from .models import Inquiry


class InquiryPendingForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['pending_inquiry', 'remarks', 'transferred_status']

    pending_inquiry = forms.ChoiceField(
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md p-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:outline-none'
        }),
    )

    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'border border-gray-300 rounded-md p-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:outline-none',
            'placeholder': 'Enter remarks',
            'rows': 8,
            'style': 'resize: none;'  
        }),
        required=True
    )

    transferred_status = forms.ChoiceField(
        choices=Employee.TRANSFER_CHOICES,  # Use the choices from your model
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md p-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:outline-none'
        }),
        required=True
    )



class InquiryActionForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['admin_action', 'remarks']

    admin_action = forms.ChoiceField(
        choices=[('close', 'close'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'border border-gray-300 rounded-md p-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:outline-none',
            'placeholder': 'Enter remarks',
            'rows': 4
        }),
        required=False
    )
