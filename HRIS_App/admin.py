from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.admin import AdminSite
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .forms import AdminEmployeeForm, NonAdminEmployeeForm
from .models import (
    Group, FunctionalGroup, Division, Wing, Region, Branch,
    Designation, Cadre, EmployeeType, EmployeeGrade, Qualification, Employee
)

@admin.register(Group)
class GroupAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name')
    list_filter = ('name', )

@admin.register(FunctionalGroup)
class FunctionalGroupAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id','name', 'group', 'allias')
    search_fields = ('id', 'name', 'group__name', 'allias')
    list_filter = ('name', 'allias')

@admin.register(Division)
class DivisionAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'division_name', 'functional_group', 'description')
    list_filter = ('division_name', 'functional_group__name')
    search_fields = ('id', 'division_name', 'functional_group__name')

@admin.register(Wing)
class WingAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name', 'division', 'description')
    search_fields = ('id', 'name', 'division__division_name')
    list_filter = ('name', 'division__division_name')

@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name', 'region_category')
    list_filter = ('name', 'region_category','functional_group__name')
    search_fields = ('id', 'name', 'region_category','functional_group__name')

@admin.register(Branch)
class BranchAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ("branch_code", 'branch_name', 'branch_region__name', 'branch_address')
    search_fields = ('id', 'branch_code', 'branch_name', 'branch_region__name')
    list_filter = ('branch_name', 'branch_region__name')

@admin.register(Designation)
class DesignationAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'title', 'description')
    search_fields = ('id', 'title')
    list_filter = ('title',)

@admin.register(Cadre)
class CadreAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name')
    list_filter = ('name', )

@admin.register(EmployeeType)
class EmployeeTypeAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name')
    list_filter = ('name', )

@admin.register(EmployeeGrade)
class EmployeeGradeAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id','grade_name', 'description')
    search_fields = ('id', 'grade_name')
    list_filter = ('grade_name', )

@admin.register(Qualification)
class QualificationAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('name', 'qualification_type', 'institution')
    search_fields = ('id', 'name', 'qualification_type', 'institution')
    list_filter = ('name', 'qualification_type', 'institution')


class EmployeeAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('SAP_ID', 'name', 'branch', 'designation', 'employee_grade', 'employee_type', 'date_of_joining', 'designation', 'is_admin_employee',)
    list_filter = ('is_admin_employee', 'is_active', 'branch')

    def get_form(self, request, obj=None, **kwargs):
        """
        Use a different form based on whether the employee is admin or non-admin.
        """
        if obj and obj.is_admin_employee:  # Use the admin employee form
            self.form = AdminEmployeeForm
        else:  # Use the non-admin employee form
            self.form = NonAdminEmployeeForm
        return super().get_form(request, obj, **kwargs)
    
admin.site.register(Employee, EmployeeAdmin)