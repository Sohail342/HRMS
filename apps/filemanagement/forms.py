from django import forms
from django.forms import DateInput
from .models import EmployeeFile, FileStatus, FileType
from apps.HRIS_App.models import Employee, Designation, Division, Branch, Region, EmployeeType

class EmployeeFileForm(forms.ModelForm):
    """Form for uploading employee files"""
    class Meta:
        model = EmployeeFile
        fields = ['employee', 'file_name', 'file_type', 'file_status', 'file', 'receiver_email', 'notes']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Select an employee'
            }),
            'file_name': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Enter a descriptive file name'
            }),
            'file_type': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Select file type'
            }),
            'file_status': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Select status'
            }),
            'file': forms.FileInput(attrs={
                'class': 'sr-only',  # Hidden but accessible for the custom file upload UI
            }),
            'receiver_email': forms.EmailInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Enter receiver\'s email address'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50',
                'placeholder': 'Add any additional notes about this file'
            }),
        }

class FileFilterForm(forms.Form):
    """Form for filtering files in the dashboard"""
    # Employee filters
    employee_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out',
        'placeholder': 'Search by employee name'
    }))
    
    employee_id = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out',
        'placeholder': 'Enter SAP ID'
    }))
    
    designation = forms.ModelChoiceField(
        queryset=Designation.objects.all(),
        required=False,
        empty_label="Select Designation",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out'
        })
    )
    
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        required=False,
        empty_label="Select Division",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out'
        })
    )
    
    branch_name = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        empty_label="Select Branch",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out'
        })
    )
    
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        empty_label="Select Region/Zone",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out'
        })
    )
    
    employment_type = forms.ModelChoiceField(
        queryset=EmployeeType.objects.all(),
        required=False,
        empty_label="Select Employment Type",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out'
        })
    )
    
    # File filters
    file_status = forms.ModelChoiceField(
        queryset=FileStatus.objects.filter(is_active=True),
        required=False,
        empty_label="Select File Status",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out'
        })
    )
    
    # Date range picker for upload date
    upload_date_start = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out',
            'placeholder': 'Start Date'
        })
    )
    
    upload_date_end = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 transition duration-150 ease-in-out',
            'placeholder': 'End Date'
        })
    )