from django.db import models



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

