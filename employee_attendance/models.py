from django.db import models
from django.contrib.auth.models import User
from HRIS_App.models import Employee
from django.conf import settings
from datetime import date, timedelta
from cloudinary.models import CloudinaryField
from django.db.models import Sum
from icecream import ic


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
    document = CloudinaryField(blank=True, null=True)
    upload_date = models.DateField(auto_now_add=True) 
    
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