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
    list_display = ('employee__name', 'application_type', 'from_date', 'to_date','leave_days','current_status', 'action_buttons',)
    list_filter = ('application_type',)
    actions = ['approve_leaves', 'decline_leaves']
    
    def leave_days(self, obj):
        # Calculate the number of leave days
        if obj.from_date and obj.to_date:
            return (obj.to_date - obj.from_date).days
        return 0
    leave_days.short_description = 'Leave Days'
    
    def current_status(self, obj):
        # Display the current status
        return obj.get_status_display()
    current_status.short_description = 'Status'
    current_status.admin_order_field = 'status'

    def action_buttons(self, obj):
        # Use Tailwind CSS classes for buttons
        return format_html(
            '<a class="px-4 py-2 bg-green-500 text-white font-bold rounded hover:bg-green-600 transition" href="{}">Approve</a> '
            '<a class="px-4 py-2 bg-red-500 text-white font-bold rounded hover:bg-red-600 transition ml-2" href="{}">Decline</a>',
            reverse('admin:approve_leave', args=[obj.pk]),
            reverse('admin:decline_leave', args=[obj.pk])
        )
    action_buttons.short_description = 'Leave Application '
    action_buttons.allow_tags = True

    # Custom actions for bulk processing
    @admin.action(description="Approve selected leave applications")
    def approve_leaves(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} leave applications were approved.")

    @admin.action(description="Decline selected leave applications")
    def decline_leaves(self, request, queryset):
        queryset.update(status='declined')
        self.message_user(request, f"{queryset.count()} leave applications were declined.")
        
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:pk>/', self.admin_site.admin_view(self.approve_leave), name='approve_leave'),
            path('decline/<int:pk>/', self.admin_site.admin_view(self.decline_leave), name='decline_leave'),
        ]
        return custom_urls + urls

    def approve_leave(self, request, pk):
        obj = self.get_object(request, pk)
        obj.status = 'approved'
        obj.save()
        self.message_user(request, f"Leave for {obj.employee.name} approved.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def decline_leave(self, request, pk):
        obj = self.get_object(request, pk)
        obj.status = 'declined'
        obj.save()
        self.message_user(request, f"Leave for {obj.employee.name} declined.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))


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