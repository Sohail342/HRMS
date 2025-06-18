from django.contrib import admin
from .models import LeaveApplication, NonInvolvementCertificate, StationaryRequest, ContractRenewal, EducationalDocument
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from .models_leave_management import EmployeeLeaveApplication, LeaveType
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect



@admin.register(LeaveType)
class AdminLeaveType(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_active=True)
    


@admin.register(EmployeeLeaveApplication)
class AdminEmployeeLeaveApplication(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', 'leave_type', 'from_date', 'to_date')
    list_filter = ('leave_type',)
    search_fields = ('employee__name', 'leave_type__name')

    def employee(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:HRIS_App_employee_change', args=[obj.employee.id]), obj.employee.name)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_view), name='export_leave_applications'),
        ]
        return custom_urls + urls

    def export_view(self, request):
        # Logic for exporting leave applications
        return HttpResponseRedirect(reverse('admin:HRIS_App_employeeleaveapplication_changelist'))

    

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