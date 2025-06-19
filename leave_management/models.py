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
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_name_display()