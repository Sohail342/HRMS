from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .models import LeaveType, EmployeeProfile, LeaveRule, LeaveEncashmentRecord, LeaveManagement, FrozenLeaveBalance, LeaveBalance


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    """Admin interface for managing leave balances."""
    list_display = ('employee', 'leave_type', 'year', 'annual_quota', 'remaining')
    search_fields = ('employee__username', 'leave_type__name')
    list_filter = ('leave_type', 'year')
    ordering = ('-year', 'employee')
    
    def get_queryset(self, request):
        """Override to filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee=request.user)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    """Admin interface for managing employee profiles."""
    list_display = ('employee', 'cadre', 'employment_type', 'contract_start_date')
    search_fields = ('employee__name', 'cadre', 'employment_type')
    list_filter = ('cadre', 'employment_type')
    ordering = ('employee__name',)
    
    def get_queryset(self, request):
        """Override to filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee=request.user)


@admin.register(LeaveManagement)
class LeaveManagementAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    """Admin interface for managing leave applications."""
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on')
    search_fields = ('employee__username', 'leave_type__name')
    list_filter = ('status', 'leave_type')
    ordering = ('-applied_on',)
    
    def get_queryset(self, request):
        """Override to filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee=request.user)

@admin.register(LeaveRule)
class LeaveRuleAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    """Admin interface for managing leave rules."""
    list_display = ('leave_type', 'cadre', 'employment_type', 'annual_quota', 'mandatory_annual_quota', 'can_freeze')
    search_fields = ('leave_type__name', 'cadre', 'employment_type')
    list_filter = ('leave_type', 'cadre', 'employment_type')
    ordering = ('leave_type', 'cadre')
    

@admin.register(FrozenLeaveBalance)
class FrozenLeaveBalanceAdmin(ModelAdmin):    
    import_form_class = ImportForm
    export_form_class = ExportForm
    """Admin interface for managing frozen leave balances."""
    list_display = ('employee', 'leave_type', 'year', 'days')
    search_fields = ('employee__username', 'leave_type__name')
    list_filter = ('leave_type', 'year')
    ordering = ('-year', 'employee')


@admin.register(LeaveEncashmentRecord)
class LeaveEncashmentRecordAdmin(ModelAdmin):   
    import_form_class = ImportForm
    export_form_class = ExportForm
    """Admin interface for managing leave encashment records."""
    list_display = ('employee', 'year', 'encashed_days', 'date_processed')
    search_fields = ('employee__name',)
    list_filter = ('year',)
    ordering = ('-year', 'employee')



@admin.register(LeaveType)
class LeaveTypeAdmin(ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    """Admin interface for managing leave types."""
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)
    
    def get_queryset(self, request):
        """Override to filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_active=True)
