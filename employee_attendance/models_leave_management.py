from django.db import models
from django.contrib.auth.models import User
from HRIS_App.models import Employee, EmployeeType
from django.conf import settings
from datetime import date, timedelta, datetime
from django.db.models import Sum
from django.core.exceptions import ValidationError


class LeavePolicy(models.Model):
    """Base model for leave policies"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class LeaveType(models.Model):
    """Model for different types of leaves (Privileged, Casual, Sick)"""
    LEAVE_TYPE_CHOICES = [
        ('Privileged', 'Privileged Leave'),
        ('Casual', 'Casual Leave'),
        ('Sick', 'Sick Leave'),
        ('Ex-Pakistan', 'Ex-Pakistan Leave'),
        ('Mandatory', 'Mandatory Leave'),
    ]
    
    name = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_name_display()


class EmployeeLeavePolicy(models.Model):
    """Model to associate leave policies with employee types"""
    employee_type = models.ForeignKey('HRIS_App.EmployeeType', on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    annual_entitlement = models.PositiveIntegerField(help_text="Annual leave entitlement in days")
    can_freeze = models.BooleanField(default=False, help_text="Whether unused leaves can be frozen for future use")
    min_consumption_required = models.PositiveIntegerField(default=0, help_text="Minimum number of days that must be consumed annually")
    carry_forward_limit = models.PositiveIntegerField(default=0, help_text="Maximum days that can be carried forward")
    carry_forward_expiry_months = models.PositiveIntegerField(default=3, help_text="Number of months after which carried forward leaves expire")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['employee_type', 'leave_type']
        verbose_name = "Employee Leave Policy"
        verbose_name_plural = "Employee Leave Policies"
    
    def __str__(self):
        return f"{self.employee_type.name} - {self.leave_type.get_name_display()} Policy"


class LeavePeriod(models.Model):
    """Model to define leave periods for different employee types"""
    employee_type = models.ForeignKey('HRIS_App.EmployeeType', on_delete=models.CASCADE)
    start_month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)])
    start_day = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 32)])
    end_month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)])
    end_day = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 32)])
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['employee_type', 'start_month', 'start_day']
    
    def __str__(self):
        return f"{self.employee_type.name} Period: {self.start_month}/{self.start_day} - {self.end_month}/{self.end_day}"
    
    def get_start_date(self, year):
        """Get the start date for a specific year"""
        return date(year, self.start_month, self.start_day)
    
    def get_end_date(self, year):
        """Get the end date for a specific year"""
        # Handle cases where end date is in the next year
        if (self.end_month < self.start_month) or (self.end_month == self.start_month and self.end_day < self.start_day):
            return date(year + 1, self.end_month, self.end_day)
        return date(year, self.end_month, self.end_day)


class EmployeeLeaveBalance(models.Model):
    """Model to track employee leave balances"""
    employee = models.ForeignKey('HRIS_App.Employee', on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    entitled_leaves = models.PositiveIntegerField(default=0)
    carried_forward_leaves = models.PositiveIntegerField(default=0)
    carried_forward_expiry_date = models.DateField(null=True, blank=True)
    used_leaves = models.PositiveIntegerField(default=0)
    frozen_leaves = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'leave_type', 'year']
    
    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.get_name_display()} Balance ({self.year})"
    
    @property
    def available_leaves(self):
        """Calculate available leaves"""
        return self.entitled_leaves + self.carried_forward_leaves - self.used_leaves
    
    @property
    def total_balance(self):
        """Calculate total balance including frozen leaves"""
        return self.available_leaves + self.frozen_leaves


class EmployeeLeaveApplication(models.Model):
    """Enhanced model for leave applications"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    
    employee = models.ForeignKey('HRIS_App.Employee', on_delete=models.CASCADE, related_name="enhanced_leave_applications")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    application_date = models.DateField(default=date.today)
    from_date = models.DateField()
    to_date = models.DateField()
    availed_leaves = models.PositiveIntegerField(default=0)
    reason = models.TextField(blank=True, null=True, help_text="Reason for leave application")
    supervisor_signature = models.CharField(max_length=100, blank=True, null=True)
    leave_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    with_station_permission = models.BooleanField(default=False, help_text="Permission to leave station")
    extension_allowed = models.BooleanField(default=False, help_text="Whether leave extension is allowed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.get_name_display()} ({self.from_date} to {self.to_date})"
    
    def save(self, *args, **kwargs):
        # Calculate availed leaves if not provided
        if not self.availed_leaves and self.from_date and self.to_date:
            self.availed_leaves = (self.to_date - self.from_date).days + 1
        
        # Validate leave balance before saving
        if self.leave_status == 'approved':
            self.validate_leave_balance()
        
        super().save(*args, **kwargs)
    
    def validate_leave_balance(self):
        """Validate if employee has sufficient leave balance"""
        current_year = date.today().year
        try:
            balance = EmployeeLeaveBalance.objects.get(
                employee=self.employee,
                leave_type=self.leave_type,
                year=current_year
            )
            
            if self.availed_leaves > balance.available_leaves:
                raise ValidationError(f"Insufficient leave balance. Available: {balance.available_leaves}, Requested: {self.availed_leaves}")
                
        except EmployeeLeaveBalance.DoesNotExist:
            # If no balance record exists, we should create one based on policy
            pass


class LeaveTransaction(models.Model):
    """Model to track leave transactions (usage, carry-forward, freezing)"""
    TRANSACTION_TYPES = [
        ('grant', 'Annual Grant'),
        ('usage', 'Leave Usage'),
        ('carry_forward', 'Carry Forward'),
        ('freeze', 'Freeze Leaves'),
        ('expire', 'Leave Expiry'),
        ('adjustment', 'Manual Adjustment'),
    ]
    
    employee = models.ForeignKey('HRIS_App.Employee', on_delete=models.CASCADE, related_name='leave_transactions')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    leave_application = models.ForeignKey(EmployeeLeaveApplication, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField(default=date.today)
    days = models.IntegerField(help_text="Positive for additions, negative for deductions")
    year = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.get_transaction_type_display()} of {abs(self.days)} {self.leave_type.get_name_display()} days"