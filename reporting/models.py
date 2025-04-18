from django.db import models
from HRIS_App.models import Employee
from cloudinary.models import CloudinaryField


class HospitalName(models.Model):
    hospital_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    logo = CloudinaryField(blank=True, null=True)


class Signature(models.Model):
    SAP_ID = models.IntegerField(blank=True, null=True)
    employee_name = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    grade = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    wing = models.CharField(max_length=100, blank=True, null=True)
    division = models.CharField(max_length=100, blank=True, null=True)
    group = models.CharField(max_length=100, blank=True, null=True)
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.employee_name



class LetterTemplates(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    template_url = CloudinaryField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee.name

