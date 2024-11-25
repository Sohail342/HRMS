from django.contrib import admin
from unfold.admin import ModelAdmin
from .resources import FunctionalGroupResource, RegionResource, BranchResource, EmployeeResource
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .forms import AdminEmployeeForm, NonAdminEmployeeForm
from django import forms
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
    resource_class  = FunctionalGroupResource
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
    resource_class = RegionResource
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('region_id', 'name', 'region_category')
    list_filter = ('name', 'region_category','functional_group__name')
    search_fields = ('region_id', 'name', 'region_category','functional_group__name')


@admin.register(Branch)
class BranchAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = BranchResource 
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ("branch_code", 'branch_name', 'region__name', 'branch_address')
    search_fields = ('id', 'branch_code', 'branch_name', 'region__name')
    list_filter = ('branch_name', 'region__name')

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
    resource_class = EmployeeResource
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('SAP_ID', 'name', 'branch', 'branch__region', 'designation', 'employee_grade', 'employee_type', 'date_of_joining', 'designation', 'is_admin_employee')
    list_filter = ('is_admin_employee', 'is_active', 'branch')

    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.is_admin_employee:  # Use the admin employee form
            self.form = AdminEmployeeForm
        else:  # Use the non-admin employee form
            self.form = NonAdminEmployeeForm

        form_class = super().get_form(request, obj, **kwargs)

        # Ensure the 'branch' field is always optional
        form_class.base_fields['branch'].required = False

        if obj and obj.branch:
            region = obj.branch.region
            if region and region.head_office:
                form_class.base_fields['branch'].widget = forms.HiddenInput()
            else:
                form_class.base_fields['branch'].queryset = Branch.objects.filter(branch_region=region)
        else:
            form_class.base_fields['branch'].queryset = Branch.objects.all()

        return form_class

    def save_model(self, request, obj, form, change):
        """
        Save the model while ensuring password handling.
        """
        # Handle the password logic
        new_password = form.cleaned_data.get('password')
        
        if change:  # If updating an existing employee
            if new_password:  # If a new password is provided
                obj.set_password(new_password)  # Hash the new password
        else:  # If creating a new employee
            if not new_password:  # If no password is provided, set the default password
                obj.set_password('1234')  # Set your desired default password here
            else:
                obj.set_password(new_password)  # Hash the new password if provided

        obj.save()


admin.site.register(Employee, EmployeeAdmin)