from django import forms
from HRIS_App.models import Employee


class InquiryPendingForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['pending_inquiry', 'remarks']

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


class TransferForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['transfer_remarks', 'transferred_status']

    transfer_remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'border border-gray-300 rounded-md p-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:outline-none',
            'placeholder': 'Enter remarks',
            'rows': 8,
            'style': 'resize: none;'  
        }),
        required=True
    )

    transferred_status = forms.ChoiceField(
        choices=Employee.TRANSFER_CHOICES,  
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md p-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:outline-none'
        }),
        required=True
    )