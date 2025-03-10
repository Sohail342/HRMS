from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .models import Signature
from unfold.admin import ModelAdmin

@admin.register(Signature)
class SignatureAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee_name', 'designation', 'grade', 'department', 'wing', 'division', 'group', 'created_at', 'updated_at']
    search_fields = ['employee_name', 'designation', 'grade', 'department', 'wing', 'division', 'group']
    list_filter = ['employee_name', 'designation', 'grade', 'department', 'wing', 'division', 'group']
    
    import_form = ImportForm
    export_form = ExportForm


