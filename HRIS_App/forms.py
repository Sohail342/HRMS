from django import forms
from .models import Employee

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
            'branch',
            'qualifications', 
            'date_of_last_promotion', 
            'date_current_posting', 
            'date_current_assignment', 
            'mobile_number', 
            'admin_signature', 
            'phone_no_official', 
            'phone_no_emergency_contact', 
            'employee_email', 
            'date_of_joining', 
            'user_group',
             
        )
    
    def clean_password(self):
        """
        Custom validation for password field to make sure that it's not empty 
        and is set when creating or updating an admin employee.
        """
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Password cannot be empty.")
        return password


class NonAdminEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('SAP_ID', 'name', 'branch', 'designation', 'employee_type',  'employee_grade', 'email', 'date_of_joining', 'designation', 'is_admin_employee',)
