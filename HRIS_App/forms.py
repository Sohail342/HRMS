from django import forms
from .models import Employee,  Branch

class AdminEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            'email', 
            'password',
            'name', 
            'is_active', 
            'is_admin', 
            'is_admin_employee', 
            'cnic_no', 
            'husband_or_father_name', 
            'SAP_ID', 
            'designation', 
            'cadre', 
            'employee_type', 
            'employee_grade', 
            'region', 
            'branch',
            'qualifications', 
            'date_of_last_promotion', 
            'date_current_posting', 
            'date_current_assignment', 
            'mobile_number', 
            'admin_signature',  
            'phone_no_emergency_contact', 
            'employee_email', 
            'date_of_joining', 
            'user_group',
            'pending_inquiry',
            'transferred_status',
            'remarks',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Condition to handle branch visibility based on region
        if self.instance and self.instance.region and self.instance.region.head_office:
            self.fields['branch'].widget = forms.HiddenInput()  # Hide the branch field if it's a head office
        else:
            # Filter branches by the selected region
            if self.instance and self.instance.region:
                self.fields['branch'].queryset = Branch.objects.filter(branch_region=self.instance.region)
            self.fields['branch'].required = False

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Password cannot be empty.")
        return password


class NonAdminEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('SAP_ID', 'name', 'region', 'branch', 'designation', 'employee_type', 
                  'employee_grade', 'email', 'date_of_joining', 'is_admin_employee', 
                  'pending_inquiry', 'remarks')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Handle branch visibility based on selected region for non-admin employees
        if self.instance and self.instance.region and self.instance.region.head_office:
            self.fields['branch'].widget = forms.HiddenInput()  # Hide branch for head office employees
        else:
            # Filter branches by region
            if self.instance and self.instance.region:
                self.fields['branch'].queryset = Branch.objects.filter(branch_region=self.instance.region)
            self.fields['branch'].required = False  