from django.contrib import admin
from unfold.admin import ModelAdmin
from .resources import FunctionalGroupResource, BranchResource, EmployeeResource, WingResource
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from .forms import AdminEmployeeForm, NonAdminEmployeeForm
from django import forms
from .models import (
    Group, FunctionalGroup, Division, Wing, Region, Branch,
    Designation, Cadre, EmployeeType, EmployeeGrade, Qualification, Employee
)

@admin.register(Group)
class GroupAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name')
    list_filter = ('name', )

@admin.register(Division)
class DivisionAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'division_name', 'description')
    list_filter = ('division_name',)
    search_fields = ('id', 'division_name',)

@admin.register(Wing)
class WingAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = WingResource
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name', 'division_name', 'description')
    search_fields = ('id', 'name', 'division__division_name')
    list_filter = ('name', 'division_name__division_name')

@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('region_id', 'name', 'region_category')
    list_filter = ('name',)
    search_fields = ('region_id', 'name', 'region_category')


@admin.register(Branch)
class BranchAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = BranchResource 
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ("branch_code", 'branch_name', 'region__name', 'branch_address', 'branch_Category')
    search_fields = ('id', 'branch_code', 'branch_name', 'region__name')
    list_filter = ('region', 'branch_Category')

@admin.register(Designation)
class DesignationAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'title')
    search_fields = ('id', 'title')
    list_filter = ('title',)

@admin.register(Cadre)
class CadreAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    list_filter = ('name', )

@admin.register(EmployeeType)
class EmployeeTypeAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('id', 'name')
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
class QualificationAdmin(ModelAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('name', 'qualification_type', 'institution')
    search_fields = ('id', 'name', 'qualification_type', 'institution')
    list_filter = ('name', 'qualification_type', 'institution')


class EmployeeAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    resource_class = EmployeeResource
    form = AdminEmployeeForm

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin and not request.user.is_superuser:
            # Allow editing only these fields for staff users
            return [field.name for field in self.model._meta.fields if field.name not in (
                                                                                        
            'email', 
            'name', 
            'is_active', 
            'in_active_reason',
            'cnic_no', 
            'husband_or_father_name', 
            'SAP_ID', 
            'designation', 
            'cadre', 
            'employee_type', 
            'employee_grade', 
            'region', 
            'branch',
            'qualifications', 
            'date_of_retirement', 
            'date_current_posting', 
            'date_current_assignment', 
            'mobile_number',   
            'employee_salutation', 
            'date_of_joining', 
            'grade_assignment',
            'pending_inquiry',
            'transferred_status',
            'remarks',
            'transfer_remarks',
            'pdf_file',
                                                                                        
            )]
        return []

    def get_fields(self, request, obj=None):
        if request.user.is_admin and not request.user.is_superuser:
            return (
                'email', 
                'name', 
                'is_active', 
                'in_active_reason',
                'cnic_no', 
                'husband_or_father_name', 
                'SAP_ID', 
                'designation', 
                'cadre', 
                'employee_type', 
                'employee_grade', 
                'region', 
                'branch',
                'qualifications', 
                'date_of_retirement', 
                'date_current_posting', 
                'date_current_assignment', 
                'mobile_number',   
                'employee_salutation', 
                'date_of_joining', 
                'grade_assignment',
                'pending_inquiry',
                'transferred_status',
                'remarks',
                'transfer_remarks',
                'pdf_file',
            )
        return super().get_fields(request, obj)

    # Explicitly include these if not using fieldsets
    filter_horizontal = ("groups", "user_permissions")

    list_display = ('SAP_ID', 'name', 'branch', 'region', 'designation', 'employee_grade', 'employee_type', 'date_of_joining', 'is_admin_employee')
    list_filter = ('designation', 'branch__region', 'is_admin_employee', 'is_active', 'branch', 'is_letter_template_admin')
    search_fields = ("SAP_ID", 'name', 'region__name', 'branch__branch_name')

    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.is_admin_employee:
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
                form_class.base_fields['branch'].queryset = Branch.objects.filter(region=region)
        else:
            form_class.base_fields['branch'].queryset = Branch.objects.all()

        return form_class

    def save_model(self, request, obj, form, change):
        """
        Save the model while ensuring password handling.
        """
        new_password = form.cleaned_data.get('password')

        if new_password:  # Check if a new password is provided
            if obj.pk:  # Check if this is an existing object (not a new one)
                # Fetch the object from the database to compare passwords
                original_obj = obj.__class__.objects.get(pk=obj.pk)

                # Check if the new password matches the current password
                if original_obj.check_password(new_password):
                    print("The new password matches the current password.")
                else:
                    print("Setting a new password.")
                    obj.set_password(new_password)  # Hash and set the new password
            else:
                # For new objects, simply set the password
                obj.set_password(new_password)
        else:
            # If no password is provided and it's an existing user, retain the current password
            if obj.pk:
                original_obj = obj.__class__.objects.get(pk=obj.pk)
                obj.password = original_obj.password

        # Save the object with the potentially updated password
        obj.save()
        
admin.site.register(Employee, EmployeeAdmin)