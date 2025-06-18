from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.contrib.admin import ModelAdmin
from .models_leave_management import (
    LeaveType,
    EmployeeLeavePolicy,
    LeavePeriod,
    EmployeeLeaveBalance,
    EmployeeLeaveApplication,
    LeaveTransaction
)


class LeaveTypeAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    search_fields = ['name', 'description']
    list_filter = ['is_active']


class EmployeeLeavePolicyAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee_type', 'leave_type', 'annual_entitlement', 'can_freeze', 'min_consumption_required', 'is_active']
    search_fields = ['employee_type__name', 'leave_type__name']
    list_filter = ['employee_type', 'leave_type', 'can_freeze', 'is_active']


class LeavePeriodAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee_type', 'start_month', 'start_day', 'end_month', 'end_day', 'is_active']
    search_fields = ['employee_type__name', 'description']
    list_filter = ['employee_type', 'start_month', 'is_active']


class EmployeeLeaveBalanceAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'entitled_leaves', 'carried_forward_leaves', 'used_leaves', 'frozen_leaves', 'available_leaves', 'total_balance']
    search_fields = ['employee__name', 'employee__SAP_ID']
    list_filter = ['leave_type', 'year']
    readonly_fields = ['available_leaves', 'total_balance']

    def available_leaves(self, obj):
        return obj.available_leaves
    
    def total_balance(self, obj):
        return obj.total_balance
    
    available_leaves.short_description = 'Available Leaves'
    total_balance.short_description = 'Total Balance'


class EmployeeLeaveApplicationAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee', 'leave_type', 'application_date', 'from_date', 'to_date', 'availed_leaves', 'leave_status']
    search_fields = ['employee__name', 'employee__SAP_ID', 'reason']
    list_filter = ['leave_type', 'leave_status', 'application_date', 'with_station_permission', 'extension_allowed']
    readonly_fields = ['availed_leaves']


class LeaveTransactionAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display = ['employee', 'leave_type', 'transaction_type', 'transaction_date', 'days', 'year']
    search_fields = ['employee__name', 'employee__SAP_ID', 'notes']
    list_filter = ['leave_type', 'transaction_type', 'year', 'transaction_date']


# Register models with their admin classes
admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(EmployeeLeavePolicy, EmployeeLeavePolicyAdmin)
admin.site.register(LeavePeriod, LeavePeriodAdmin)
admin.site.register(EmployeeLeaveBalance, EmployeeLeaveBalanceAdmin)
admin.site.register(EmployeeLeaveApplication, EmployeeLeaveApplicationAdmin)
admin.site.register(LeaveTransaction, LeaveTransactionAdmin)