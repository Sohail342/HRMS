from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

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
    list_display = ('employee', 'leave_type', 'year', 'annual_quota', 'remaining')
    search_fields = ('employee__name', 'leave_type__name')
    list_filter = ('leave_type', 'year')
    ordering = ('-year', 'employee')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(employee=request.user)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', 'cadre', 'employment_type', 'contract_start_date', show_encashment_eligibility)
    search_fields = ('employee__name', 'cadre', 'employment_type')
    list_filter = ('cadre', 'employment_type')
    ordering = ('employee__name',)
    actions = [assign_balances, freeze_leaves, expire_privileged]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(employee=request.user)


@admin.register(LeaveManagement)
class LeaveManagementAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on')
    search_fields = ('employee__name', 'leave_type__name')
    list_filter = ('status', 'leave_type')
    ordering = ('-applied_on',)

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
    list_display = ('employee', 'leave_type', 'year', 'days')
    search_fields = ('employee__name', 'leave_type__name')
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
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(is_active=True)
