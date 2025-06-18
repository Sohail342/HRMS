from django import forms
from HRIS_App.custom_forms import RequiredOptionalFieldsModelForm
from .models_leave_management import (
    LeaveType,
    EmployeeLeavePolicy,
    LeavePeriod,
    EmployeeLeaveBalance,
    EmployeeLeaveApplication,
    LeaveTransaction
)
from datetime import date, timedelta
from django.core.exceptions import ValidationError


class LeaveApplicationForm(RequiredOptionalFieldsModelForm):
    """Form for leave applications with validation for leave balance"""
    class Meta:
        model = EmployeeLeaveApplication
        fields = ['leave_type', 'from_date', 'to_date', 'reason', 'with_station_permission', 'extension_allowed']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        leave_type = cleaned_data.get('leave_type')
        
        if from_date and to_date:
            # Validate date range
            if from_date > to_date:
                raise ValidationError("From Date cannot be later than To Date.")
            
            # Calculate availed leaves
            availed_leaves = (to_date - from_date).days + 1
            cleaned_data['availed_leaves'] = availed_leaves
            
            # Validate leave balance if employee is provided
            if self.employee and leave_type:
                current_year = date.today().year
                try:
                    balance = EmployeeLeaveBalance.objects.get(
                        employee=self.employee,
                        leave_type=leave_type,
                        year=current_year
                    )
                    
                    if availed_leaves > balance.available_leaves:
                        raise ValidationError({
                            'leave_type': f"Insufficient leave balance. Available: {balance.available_leaves}, Requested: {availed_leaves}"
                        })
                        
                except EmployeeLeaveBalance.DoesNotExist:
                    # If no balance record exists, we'll handle this in the view
                    pass
        
        return cleaned_data


class LeaveBalanceAdjustmentForm(forms.Form):
    """Form for manual adjustment of leave balances"""
    ADJUSTMENT_TYPES = [
        ('add', 'Add Leaves'),
        ('deduct', 'Deduct Leaves'),
        ('freeze', 'Freeze Leaves'),
        ('unfreeze', 'Unfreeze Leaves'),
    ]
    
    employee = forms.ModelChoiceField(queryset=None)
    leave_type = forms.ModelChoiceField(queryset=None)
    adjustment_type = forms.ChoiceField(choices=ADJUSTMENT_TYPES)
    days = forms.IntegerField(min_value=1)
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    
    def __init__(self, *args, **kwargs):
        from HRIS_App.models import Employee
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)
        self.fields['leave_type'].queryset = LeaveType.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        leave_type = cleaned_data.get('leave_type')
        adjustment_type = cleaned_data.get('adjustment_type')
        days = cleaned_data.get('days')
        
        if employee and leave_type and adjustment_type and days:
            current_year = date.today().year
            
            try:
                balance = EmployeeLeaveBalance.objects.get(
                    employee=employee,
                    leave_type=leave_type,
                    year=current_year
                )
                
                # Validate deduction and unfreezing operations
                if adjustment_type == 'deduct' and days > balance.available_leaves:
                    raise ValidationError({
                        'days': f"Cannot deduct more than available leaves. Available: {balance.available_leaves}"
                    })
                
                if adjustment_type == 'unfreeze' and days > balance.frozen_leaves:
                    raise ValidationError({
                        'days': f"Cannot unfreeze more than frozen leaves. Frozen: {balance.frozen_leaves}"
                    })
                    
                if adjustment_type == 'freeze' and days > balance.available_leaves:
                    raise ValidationError({
                        'days': f"Cannot freeze more than available leaves. Available: {balance.available_leaves}"
                    })
                    
            except EmployeeLeaveBalance.DoesNotExist:
                # If no balance record exists, we can only add leaves
                if adjustment_type in ['deduct', 'freeze', 'unfreeze']:
                    raise ValidationError({
                        'adjustment_type': f"No leave balance record exists for this employee and leave type. You can only add leaves."
                    })
        
        return cleaned_data


class LeaveTypeForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'description', 'is_active']


class EmployeeLeavePolicyForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = EmployeeLeavePolicy
        fields = [
            'employee_type', 'leave_type', 'annual_entitlement', 'can_freeze',
            'min_consumption_required', 'carry_forward_limit', 'carry_forward_expiry_months',
            'is_active'
        ]


class LeavePeriodForm(RequiredOptionalFieldsModelForm):
    class Meta:
        model = LeavePeriod
        fields = ['employee_type', 'start_month', 'start_day', 'end_month', 'end_day', 'description', 'is_active']
    
    def clean(self):
        cleaned_data = super().clean()
        start_month = cleaned_data.get('start_month')
        start_day = cleaned_data.get('start_day')
        end_month = cleaned_data.get('end_month')
        end_day = cleaned_data.get('end_day')
        
        # Validate day values for each month
        if start_month and start_day:
            if start_month in [4, 6, 9, 11] and start_day > 30:
                raise ValidationError({'start_day': f"Month {start_month} has only 30 days."})
            elif start_month == 2 and start_day > 29:
                raise ValidationError({'start_day': "February has at most 29 days."})
        
        if end_month and end_day:
            if end_month in [4, 6, 9, 11] and end_day > 30:
                raise ValidationError({'end_day': f"Month {end_month} has only 30 days."})
            elif end_month == 2 and end_day > 29:
                raise ValidationError({'end_day': "February has at most 29 days."})
        
        return cleaned_data