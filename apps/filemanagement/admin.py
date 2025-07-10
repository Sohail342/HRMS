from django.contrib import admin
from .models import FileStatus, FileType, EmployeeFile

@admin.register(FileStatus)
class FileStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'allowed_extensions', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(EmployeeFile)
class EmployeeFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'employee', 'file_type', 'file_status', 'upload_timestamp', 'receiver_email')
    list_filter = ('file_status', 'file_type', 'upload_timestamp')
    search_fields = ('file_name', 'employee__name', 'employee__SAP_ID', 'receiver_email')
    date_hierarchy = 'upload_timestamp'
    raw_id_fields = ('employee', 'created_by')