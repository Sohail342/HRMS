from django.db import models
from cloudinary.models import CloudinaryField
from apps.HRIS_App.models import Employee

class FileStatus(models.Model):
    """Model for file status types"""
    name = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=20, help_text="Color code for the status badge (e.g., 'green-500')")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "File Status"
        verbose_name_plural = "File Statuses"

class FileType(models.Model):
    """Model for different types of files"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    allowed_extensions = models.CharField(max_length=100, help_text="Comma-separated list of allowed file extensions")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class EmployeeFile(models.Model):
    """Model for managing employee files"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)
    file_type = models.ForeignKey(FileType, on_delete=models.SET_NULL, null=True)
    file_status = models.ForeignKey(FileStatus, on_delete=models.SET_NULL, null=True)
    file = CloudinaryField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    receiver_email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Tracking fields
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_files')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.file_name}"
    
    class Meta:
        ordering = ['-upload_timestamp']