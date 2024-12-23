from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .models import RicpData, RicpKPI

@admin.register(RicpData)
class RicpDataAdmnin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', 'half_year_review', 'full_year_review', 'final_score')
    


@admin.register(RicpKPI)
class RicpKPIAdmnin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('ricp_data',  'kpi', 'achievement', 'weightage', 'target_date', 'score')
    
