from django.contrib import admin
from .models import LeaveApplication, NonInvolvementCertificate, StationaryRequest, ContractRenewal, EducationalDocument
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect


# Register your models here.
@admin.register(LeaveApplication)
class AdminLeaveApplication(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee__name', 'application_type', 'from_date', 'to_date')
    list_filter = ('application_type',)

    
   


# ---------------------------------------------------------------------------------------------------------

@admin.register(NonInvolvementCertificate)
class AdminNonInvolvementCertificate(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee__name', 'reason', 'request_date',)
    

@admin.register(StationaryRequest)
class AdminStationaryRequest(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee__name', 'item_name','quantity','reason_for_request', 'request_date',)
    

@admin.register(ContractRenewal)
class AdminContractRenewal(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee__name', 'position','reason','contract_expiry_date',)
    
@admin.register(EducationalDocument)
class AdminEducationalDocument(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display =('employee__name', 'document_type','upload_date',)