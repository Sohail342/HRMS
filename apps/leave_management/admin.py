from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .resources import FrozenLeaveBalanceResource, LeavebalanceResource
from .models import (
    LeaveType, EmployeeProfile, LeaveRule, LeaveEncashmentRecord,
    LeaveManagement, FrozenLeaveBalance, LeaveBalance
)
from .leave_utils import (
    assign_all_employee_leave_balances,
    freeze_and_carry_forward_leaves,
    expire_privileged_leaves,
    is_eligible_for_encashment,
)
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from datetime import datetime


# --- Admin Actions ---

@admin.action(description="Assign Leave Balances for All Employees")
def assign_balances(modeladmin, request, queryset):
    assign_all_employee_leave_balances()
    messages.success(request, "Leave balances assigned successfully.")


@admin.action(description="Freeze & Carry Forward Sick Leaves for Current Year")
def freeze_leaves(modeladmin, request, queryset):
    freeze_and_carry_forward_leaves(datetime.now().year)
    messages.success(request, "Sick leaves frozen and carried forward.")


@admin.action(description="Expire Privileged Leaves (After March 31)")
def expire_privileged(modeladmin, request, queryset):
    expire_privileged_leaves()
    messages.success(request, "Privileged leaves expired.")


@admin.display(description="Encashment Eligible?")
def show_encashment_eligibility(obj):
    return "✅ Yes" if is_eligible_for_encashment(obj.employee) else "❌ No"


# --- Admin Registrations ---

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    resource_class = LeavebalanceResource
    list_display = ('employee', 'employee__SAP_ID', 'leave_type', 'year', 'annual_quota', 'remaining', 'mandatory_remaining')
    search_fields = ('employee__name', 'leave_type__name', 'employee__SAP_ID')
    list_filter = ('leave_type', 'year')
    ordering = ('-year', 'employee')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(employee=request.user)
    


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', "employee__SAP_ID", 'cadre', 'employment_type', 'contract_start_date', show_encashment_eligibility)
    search_fields = ('employee__name', 'cadre', 'employment_type')
    list_filter = ('cadre', 'employment_type')
    ordering = ('employee__name',)
    actions = [assign_balances, freeze_leaves, expire_privileged]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(employee=request.user)


class RejectLeaveForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, required=True, help_text="Please provide a reason for rejecting this leave application.")


@admin.action(description="Approve selected leave applications")
def approve_leave(modeladmin, request, queryset):
    updated = queryset.update(status='Approved')
    messages.success(request, f"{updated} leave application(s) have been approved.")


@admin.action(description="Reject selected leave applications")
def reject_leave(modeladmin, request, queryset):
    # If this is a POST request, process the form data
    if 'apply' in request.POST:
        form = RejectLeaveForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            # Update all selected leave applications
            count = 0
            for leave in queryset:
                leave.status = 'Rejected'
                leave.reason = reason
                leave.save()
                count += 1
            messages.success(request, f"{count} leave application(s) have been rejected.")
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = RejectLeaveForm()

    # If this is a GET request or the form is invalid, display the form
    return render(
        request,
        'admin/leave_management/reject_leave.html',
        context={
            'leaves': queryset,
            'form': form,
            'title': 'Reject Leave Applications',
        }
    )


@admin.register(LeaveManagement)
class LeaveManagementAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on', 'action_buttons')
    search_fields = ('employee__name', 'leave_type__name')
    list_filter = ('status', 'leave_type')
    ordering = ('-applied_on',)
    change_list_template = 'admin/leave_management/leavemanagement_change_list.html'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/', self.admin_site.admin_view(self.approve_view), name='leave_management_leavemanagement_approve'),
            path('<path:object_id>/reject/', self.admin_site.admin_view(self.reject_view), name='leave_management_leavemanagement_reject'),
        ]
        return custom_urls + urls
    
    def approve_view(self, request, object_id):
        leave = self.get_object(request, object_id)
        if leave:
            leave.status = 'Approved'
            leave.save()
            messages.success(request, f"Leave application for {leave.employee} has been approved.")
        return HttpResponseRedirect("../../../")
    
    def reject_view(self, request, object_id):
        leave = self.get_object(request, object_id)
        if leave and request.method == 'POST':
            form = RejectLeaveForm(request.POST)
            if form.is_valid():
                leave.status = 'Rejected'
                leave.reason = form.cleaned_data['reason']
                leave.save()
                messages.success(request, f"Leave application for {leave.employee} has been rejected.")
                return HttpResponseRedirect("../../../")
        else:
            form = RejectLeaveForm()
        
        return render(
            request,
            'admin/leave_management/reject_leave_individual.html',
            context={
                'leave': leave,
                'form': form,
                'title': 'Reject Leave Application',
                'opts': self.model._meta,
            }
        )
    
    @admin.display(description="Actions")
    def action_buttons(self, obj):
        from django.utils.html import format_html
        if obj.status == 'Pending':
            approve_url = f"<a href='{obj.pk}/approve/' class='action-button approve-button'>Approve</a>"
            reject_url = f"<a href='{obj.pk}/reject/' class='action-button reject-button'>Reject</a>"
            return format_html(f"{approve_url} {reject_url}")
        return format_html("")
    
    # Note: allow_tags is deprecated in newer Django versions, using format_html instead

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(employee=request.user)


@admin.register(LeaveRule)
class LeaveRuleAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('leave_type', 'cadre', 'employment_type', 'annual_quota', 'mandatory_annual_quota', 'can_freeze')
    search_fields = ('leave_type__name', 'cadre', 'employment_type')
    list_filter = ('leave_type', 'cadre', 'employment_type')
    ordering = ('leave_type', 'cadre')


@admin.register(FrozenLeaveBalance)
class FrozenLeaveBalanceAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    resource_class = FrozenLeaveBalanceResource
    list_display = ('employee', 'employee__SAP_ID', 'leave_type', 'year', 'days')
    search_fields = ('employee__name', 'leave_type__name', 'employee__SAP_ID')
    list_filter = ('leave_type', 'year')
    ordering = ('-year', 'employee')


@admin.register(LeaveEncashmentRecord)
class LeaveEncashmentRecordAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', 'year', 'encashed_days', 'date_processed')
    search_fields = ('employee__name',)
    list_filter = ('year',)
    ordering = ('-year', 'employee')


@admin.register(LeaveType)
class LeaveTypeAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('name', 'is_mandatory_leave', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(is_active=True)
