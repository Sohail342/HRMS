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


class Purpose(models.Model):
    purpose_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.purpose_name
    
    class Meta:
        verbose_name = "Purpose"
        verbose_name_plural = "Purposes"


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
    template_saved_url = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee.name
    
    
class PermenantLetterTemplates(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, blank=True, null=True)
    template_url = CloudinaryField(blank=True, null=True)
    template_saved_url = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee.name


class FamilyMember(models.Model):
    RELATION_CHOICES = [
        ('Father of', 'Father of'),
        ('Mother of', 'Mother of'),
        ('Son of', 'Son of'),
        ('Daughter of', 'Daughter of'),
        ('Wife of', 'Wife of'),
        ('Husband of', 'Husband of'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='family_members')
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=13)
    age = models.PositiveIntegerField(blank=True, null=True, default=0)
    marital_status = models.BooleanField(default=False, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.relation} {self.employee.name}"


class HospitalizationForm(models.Model):
    CATEGORY_CHOICES = [
        ('Self', 'Self'),
        ('Family/Dependents', 'Family/Dependents'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='hospitalization_forms')
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    family_member = models.ForeignKey(FamilyMember, on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.ForeignKey(Purpose, on_delete=models.SET_NULL, null=True, blank=True)
    hospital_name = models.CharField(max_length=100)
    pdf_url = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.category_type == 'Self':
            return f"Hospitalization for {self.employee.name}"
        else:
            return f"Hospitalization for {self.family_member.name} - {self.family_member.relation} {self.employee.name}"



class PulicHolidays(models.Model):
    day = models.CharField(unique=True, blank=True, null=True)
    date = models.DateField(unique=True, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.day if self.day else "Public Holiday"
    class Meta:
        verbose_name = "Public Holiday"
        verbose_name_plural = "Public Holidays"
        ordering = ['date']