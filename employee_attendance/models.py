from django.db import models
from django.contrib.auth.models import User
from HRIS_App.models import Employee
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Sum
from icecream import ic




#--------------------------- Permenant Employee Leave Management --------------------------------------------
class PermanentLeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    total_leaves = models.PositiveIntegerField(default=0)  

    def __str__(self):
        return self.name


class LeaveRecordPremanent(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_record_Premanent")
    leave_type = models.ForeignKey(PermanentLeaveType, on_delete=models.CASCADE)
    availed_leaves = models.PositiveIntegerField(default=0)  # Leaves taken by the employee

    @property
    def remaining_leaves(self):
        return self.leave_type.total_leaves - self.availed_leaves

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name}" 
    
class LeaveApplication(models.Model):
    LEAVE_CHOICES = [
        ('Casual', 'Casual Leave'),
        ('Privilege', 'Privilege Leave'),
        ('Sick', 'Sick Leave'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_applications")
    leave_date = models.DateField(default=None, blank=True, null=True)  
    from_date = models.DateField(default=None, blank=True, null=True)
    to_date = models.DateField(default=None, blank=True, null=True) 
    availed_leaves = models.IntegerField(default=0, blank=True, null=True)
    reason = models.TextField(default=None, blank=True, null=True)
    application_type = models.CharField(max_length=100, choices=LEAVE_CHOICES)
    supervisor_signature = models.CharField(max_length=100)

    def __str__(self):
        return f"Leave Request from {self.employee.name} for {self.leave_date}"
    
    def save(self, *args, **kwargs):
        # Ensure from_date and to_date are provided
        if self.from_date and self.to_date:
            # Calculate the number of days for the current leave
            self.availed_leaves = (self.to_date - self.from_date).days 

            # Get the total availed leaves so far for this user and application type
            total_previous_leaves = LeaveApplication.objects.filter(
                employee=self.employee, 
                application_type=self.application_type
            ).exclude(id=self.id).aggregate(total=Sum('availed_leaves'))['total'] or 0

            # Calculate the total leaves after including the current leave
            total_leaves = total_previous_leaves + self.availed_leaves

            # Raise an error if the total leaves exceed the allowed limit (e.g., 20)
            if total_leaves > 20:
                raise ValueError("Total availed leave days cannot exceed 20 days")

        # Call the parent save method
        super().save(*args, **kwargs)
    
    
    
#--------------------------- Contractual Employee Leave Management --------------------------------------------

class ContractualLeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    total_leaves = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ContractualLeaveApplication(models.Model):
    LEAVE_CHOICES = [
        ('Casual', 'Casual Leave'),
        ('Sick', 'Sick Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contractual_leave_applications")
    leave_date = models.DateField()  
    from_date = models.DateField()
    to_date = models.DateField() 
    reason = models.TextField()
    application_type = models.CharField(max_length=100, choices=LEAVE_CHOICES)
    supervisor_signature = models.CharField(max_length=100)

    def __str__(self):
        return f"Leave Request from {self.employee.name} for {self.leave_date}"
    
class ContractualLeaveRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contractual_leave_record")
    availed_leaves = models.PositiveIntegerField(default=0)
    application_type = models.ForeignKey(ContractualLeaveApplication, on_delete=models.CASCADE, choices=ContractualLeaveApplication.LEAVE_CHOICES)

    @property
    def remaining_leaves(self):
        return self.application_type.total_leaves - self.availed_leaves

    def __str__(self):
        return f"{self.employee.name} - {self.application_type.name}"



class LeaveRecordContractual(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50, choices=[('Casual', 'Casual'), ('Sick', 'Sick'), ('Privilege', 'Privilege')])
    days_taken = models.IntegerField()
    leave_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Approved', 'Approved'), ('Pending', 'Pending'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return f"{self.employee} - {self.leave_type} - {self.leave_date}"



#--------------------------- Non-Involvement Certificate Request ------------------------------------

class NonInvolvementCertificate(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="non_involvement_certificates")
    request_date = models.DateField()
    reason = models.TextField()
    supporting_docs = models.FileField(upload_to="non_involvement_certificates/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Non-Involvement Certificate - {self.employee.name}"
    


#----------------------------- Educational Document Upload -------------------------------------------
    
class EducationalDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="educational_documents")
    document_type = models.CharField(max_length=100)
    document = models.FileField(upload_to="educational_documents/")
    upload_date = models.DateField(auto_now_add=True)  # Automatically sets the upload date to current date
    
    def __str__(self):
        return f"{self.employee.name} - {self.document_type}"



#----------------------------- Contract Renewal Request ------------------------------------
    
class ContractRenewal(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contract_renewals")
    position = models.CharField(max_length=100)
    reason = models.TextField()
    renewal_document = models.FileField(upload_to="renewal_documents/")
    contract_expiry_date = models.DateField()

    def __str__(self):
        return f"Contract Renewal Request from {self.employee.name} for {self.renewal_date}"


#------------------------------ Stationary Request ----------------------------------------------

class StationaryRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="stationary_requests")
    item_name= models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    reason_for_request = models.TextField()
    request_date = models.DateField()

    def __str__(self):
        return f"Stationary Request from {self.employee.name} for {self.item_name}"