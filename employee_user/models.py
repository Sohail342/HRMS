from django.db import models
from HRIS_App.models import Employee

class RicpData(models.Model):
    """
    This model represents the overall Risk, Internal Controls & Processes (RICP) data for an employee.
    """
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="ricp_data")
    half_year_review = models.CharField(max_length=20, blank=True, null=True)
    full_year_review = models.CharField(max_length=20, blank=True, null=True)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    

    def __str__(self):
        return f"RICP Data for {self.employee}"
    
    class Meta:
        verbose_name = "Risk, Internal Controls & Processes"


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

    def __str__(self):
        return f"KPI: {self.kpi} for {self.ricp_data.employee}"
    
    class Meta:
        verbose_name = "RICP KPI"
