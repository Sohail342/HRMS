from django.db import models
from HRIS_App.models import Employee

class RicpData(models.Model):
    """
    This model represents the overall Risk, Internal Controls & Processes (RICP) data for an employee.
    """
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="ricp_data")
    half_year_review = models.CharField(max_length=20, blank=True, null=True)
    full_year_review = models.CharField(max_length=20, blank=True, null=True)
    
    

    def __str__(self):
        return f"RICP Data for {self.employee}"
    
    class Meta:
        verbose_name = "Balance ScoreCard Employee"


class RicpKPI(models.Model):
    """
    This model represents each KPI (Key Performance Indicator) associated with an employee's RICP data.
    """
    ricp_data = models.ForeignKey(RicpData, on_delete=models.CASCADE, related_name="kpis")
    kpi = models.TextField()
    achievement = models.TextField()
    weightage = models.CharField(max_length=10, blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    score = models.PositiveIntegerField(blank=True, null=True)
    bsc_form_type = models.CharField(max_length=100, default=None, blank=True, null=True)
    form_final_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"KPI: {self.kpi} for {self.ricp_data.employee}"
    
    class Meta:
        verbose_name = "Balance ScoreCard Form"


class DeletedEmployees(models.Model):
    """
    This model stores information about employees that have been deleted from the system.
    """
    resign_choices = [
        ("Resigned", "Resigned"),
        ("Transfered out of Group", "Transfered out of Group"),
        ("Deceased", "Deceased"),
        ("Retired", "Retired"),
        ("Terminated", "Terminated"),
        ("Suspended", "Suspended"),
        ("Contract Expired", "Contract Expired"),
        ("Other", "Other"),
    ]
    sap_id = models.IntegerField(unique=True, verbose_name="SAP ID")
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=500, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True, choices=resign_choices)
    employee_grade = models.CharField(max_length=100, blank=True, null=True)
    employee_type = models.CharField(max_length=100, blank=True, null=True)
    date_of_joining = models.CharField(max_length=100, blank=True, null=True)
    deletion_reason = models.TextField(blank=True, null=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="deleted_employees")

    def __str__(self):
        return f"Deleted Employee: {self.name} (SAP ID: {self.sap_id})"
    
    class Meta:
        verbose_name = "Deleted Employee"
        verbose_name_plural = "Deleted Employees"
        ordering = ["-deleted_at"]
