from django.db import models

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
    is_freezable = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_name_display()
    

class EmployeeProfile(models.Model):
    """Model for employee profile to store cadre and employment type"""
    
    EMPLOYEE_CADRE_CHOICES = [
        ('Officer', 'Officer'),
        ('Executive', 'Executive'),
        ('Clerical', 'Clerical'),
        ('Non-Clerical', 'Non-Clerical'),
    ]
    EMPLOYMENT_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Contractual', 'Contractual'),
    ]

    employee = models.OneToOneField('HRIS_App.Employee', on_delete=models.CASCADE)
    cadre = models.CharField(max_length=20, choices=EMPLOYEE_CADRE_CHOICES)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    contract_start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.cadre} ({self.employment_type})"



class LeaveRule(models.Model):
    """Model for defining leave rules based on employee cadre and employment type"""

    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    cadre = models.CharField(max_length=20, choices=EmployeeProfile.EMPLOYEE_CADRE_CHOICES)
    employment_type = models.CharField(max_length=20, choices=EmployeeProfile.EMPLOYMENT_TYPE_CHOICES)
    annual_quota = models.PositiveIntegerField()
    mandatory_annual_quota = models.PositiveIntegerField(default=0)  # for mandatory leave
    can_freeze = models.BooleanField(default=False)
    carry_forward_deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.leave_type.name} - {self.cadre} ({self.employment_type})"
    


class LeaveBalance(models.Model):
    employee = models.ForeignKey("HRIS_App.Employee", on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    annual_quota = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name} ({self.remaining}/{self.annual_quota})"



class LeaveManagement(models.Model):
    """Model for managing leave applications"""

    employee = models.ForeignKey("HRIS_App.Employee", on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Approved, Rejected
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name} ({self.status})"

    @property
    def leave_days(self):
        return (self.end_date - self.start_date).days + 1
    

class FrozenLeaveBalance(models.Model):
    employee = models.ForeignKey("HRIS_App.Employee", on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    days = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name} ({self.year})"



class LeaveEncashmentRecord(models.Model):
    employee = models.ForeignKey("HRIS_App.Employee", on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    encashed_days = models.PositiveIntegerField()
    date_processed = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.year} - {self.encashed_days} days"
    