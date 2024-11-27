from django import forms
from .models import Employee,  Branch

class AdminEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            'email', 
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
            'date_of_joining', 
            'grade_assignment',
            'pending_inquiry',
            'transferred_status',
            'remarks',
            'transfer_remarks',
        )

    def clean_password(self):
        # If no password is provided, return None to avoid overwriting
        password = self.cleaned_data.get('password')
        if password == "":
            return None
        return password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Condition to handle branch visibility based on region
        if self.instance and self.instance.region and self.instance.region.head_office:
            self.fields['branch'].widget = forms.HiddenInput()  # Hide the branch field if it's a head office
        else:
            # Filter branches by the selected region
            if self.instance and self.instance.region:
                self.fields['branch'].queryset = Branch.objects.filter(region=self.instance.region)
            self.fields['branch'].required = False

    def save_model(self, request, obj, form, change):
        """
        Save the model while ensuring password handling.
        """
        # Handle the password logic
        new_password = form.cleaned_data.get('password')
        
        if change:  # Updating an existing employee
            if new_password:  # If a new password is provided
                obj.set_password(new_password)  # Hash and set the new password
        else:  # Creating a new employee
            if not new_password:  # If no password is provided, set the default password
                obj.set_password('1234')  # Default password for new employees
            else:
                obj.set_password(new_password)  # Hash the provided password

        obj.save()





class NonAdminEmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ('SAP_ID', 'name', 'region', 'branch', 'designation', 'employee_type', 
                  'employee_grade', 'email', 'date_of_joining', 'is_admin_employee', 'grade_assignment',
                  'pending_inquiry', 'remarks', 'transfer_remarks')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Handle branch visibility based on selected region for non-admin employees
        if self.instance and self.instance.region and self.instance.region.head_office:
            self.fields['branch'].widget = forms.HiddenInput()  # Hide branch for head office employees
        else:
            # Filter branches by region
            if self.instance and self.instance.region:
                self.fields['branch'].queryset = Branch.objects.filter(region=self.instance.region)
            self.fields['branch'].required = False  


class AssignGradeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['grade_assignment']

    
    grade_assignment = forms.ChoiceField(
        choices=Employee.GRADE_CHOICES,  
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md p-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:outline-none'
        }),
        required=True
    )