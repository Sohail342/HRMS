from django import forms
from .models import Employee, Branch
from .custom_forms import RequiredOptionalFieldsModelForm
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple

class AdminEmployeeForm(RequiredOptionalFieldsModelForm):
    # Fields to manage groups and permissions
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Groups", is_stacked=False)
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("User permissions", is_stacked=False)
    )

    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep the current password.")
    class Meta:
        model = Employee
        fields = (
            'SAP_ID', 
            'name', 
            'email', 
            'password',
            'cnic_no', 
            'husband_or_father_name', 
            'designation', 
            'division',
            'wing', 
            'cadre', 
            'employee_type', 
            'employee_grade', 
            'region', 
            'branch',
            'iban',
            'qualifications', 
            'mobile_number', 
            'admin_signature',  
            'employee_salutation', 
            'grade_assignment',
            'pending_inquiry',
            'transferred_status',
            'remarks',
            'transfer_remarks',

            'birth_date',
            'date_of_joining', 
            'date_of_retirement', 
            'date_of_contract_expiry',
            'date_current_posting', 
            'date_current_assignment',
            'date_of_last_promotion', 

            'job_description',
            'successor',
            'is_superuser',
            'is_active', 
            'in_active_reason',
            'is_letter_template_admin',
            'is_admin_employee', 
            'is_admin', 
            'pdf_file',
        )

    def clean_password(self):
        """
        Return the cleaned password only if it is provided; otherwise, return None.
        """
        
        password = self.cleaned_data.get('password')
        if password:
            return password
        return None 

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



class NonAdminEmployeeForm(RequiredOptionalFieldsModelForm):

    class Meta:
        model = Employee
        fields = (
            'SAP_ID', 
            'name', 
            'email', 
            'cnic_no', 
            'husband_or_father_name', 
            'wing', 
            'designation',
            'division', 
            'cadre', 
            'employee_type', 
            'employee_grade', 
            'region', 
            'branch',
            'iban',
            'qualifications', 
            'mobile_number', 
            'employee_salutation',  
            'grade_assignment',
            'pending_inquiry',
            'transferred_status',
            'remarks',
            'transfer_remarks',

            'birth_date',
            'date_of_joining', 
            'date_of_retirement', 
            'date_of_contract_expiry',
            'date_current_posting', 
            'date_current_assignment',
            'date_of_last_promotion', 


            'job_description',
            'successor',
            'admin_signature',  
            'is_active', 
            'in_active_reason',
            'is_admin_employee', 
            'is_superuser',
            'pdf_file',
        )

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



class AssignGradeForm(RequiredOptionalFieldsModelForm):
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