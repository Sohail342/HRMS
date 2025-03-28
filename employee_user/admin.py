from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .models import RicpData, RicpKPI

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
