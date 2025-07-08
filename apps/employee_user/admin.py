from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .models import RicpData, RicpKPI, DeletedEmployees

@admin.register(RicpData)
class RicpDataAdmnin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', )
    
    


@admin.register(RicpKPI)
class RicpKPIAdmnin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('ricp_data__employee',  'bsc_form_type', 'weightage', 'target_date', 'score', 'form_final_score')
    readonly_fields = ('weightage', 'bsc_form_type')


@admin.register(DeletedEmployees)
class DeletedEmployeesAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('sap_id', 'name', 'designation', 'branch', 'region', 'deleted_at', 'deleted_by')
    search_fields = ('sap_id', 'name', 'email', 'designation', 'branch', 'region')
    list_filter = ('region', 'employee_grade', 'employee_type', 'deleted_at')
    readonly_fields = ('sap_id', 'name', 'email', 'designation', 'branch', 'region', 'employee_grade', 
                      'employee_type', 'date_of_joining', 'deleted_at', 'deleted_by')
    fieldsets = (
        ('Employee Information', {
            'fields': ('sap_id', 'name', 'email', 'designation', 'branch', 'region', 'employee_grade', 'employee_type', 'date_of_joining')
        }),
        ('Deletion Information', {
            'fields': ('deletion_reason', 'deleted_at', 'deleted_by')
        }),
    )
