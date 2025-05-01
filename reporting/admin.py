from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .models import Signature, LetterTemplates, HospitalName, PermenantLetterTemplates
from unfold.admin import ModelAdmin


@admin.register(HospitalName)
class HospitalNameAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['hospital_name']
    search_fields = ['hospital_name']
    list_filter = ['hospital_name']

@admin.register(Signature)
class SignatureAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee_name', 'designation', 'grade', 'department', 'wing', 'division', 'group', 'created_at', 'updated_at']
    search_fields = ['employee_name', 'designation', 'grade', 'department', 'wing', 'division', 'group']
    list_filter = ['employee_name', 'designation', 'grade', 'department', 'wing', 'division', 'group']
    
    import_form = ImportForm
    export_form = ExportForm

@admin.register(LetterTemplates)
class LetterTemplatesAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee']
    
    
@admin.register(PermenantLetterTemplates)
class PermenantLetterTemplatesAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee', 'description']
    search_fields = ['employee', 'description']


