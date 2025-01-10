from django.contrib import admin
from .models import LeaveApplication
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

# Register your models here.
@admin.register(LeaveApplication)
class AdminLeaveApplication(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee__name', 'application_type', 'leave_date',)
    list_filter = ('leave_date', )