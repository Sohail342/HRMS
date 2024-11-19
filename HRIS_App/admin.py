from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.admin import AdminSite
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm
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

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin, ModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ('SAP_ID', 'full_name', 'designation', 'branch', 'cadre', 'employee_type', 'employee_grade')
    search_fields = ('SAP_ID', 'full_name', 'cnic_no', 'mobile_no', 'employee_email', 'designation__title', 'cadre__name', 'employee_type__name', 'employee_grade__grade_name', 'branch__branch_name')
    list_filter = ('designation__title', 'cadre__name', 'employee_type__name', 'employee_grade__grade_name', 'branch__branch_name')


#  Ordering Models
# class CustomAdminSite(AdminSite):
#     def get_app_list(self, request):
#         """
#         Return a sorted list of all the installed apps that have been
#         registered in this site.
#         """
#         # Define the ordering for models
#         ordering = {
#             "Group": 1,
#             "FunctionalGroup": 2,
#             "Division": 3,
#             "Wing": 4,
#             "Region": 5,
#             "Branch": 6,
#             "Designation": 7,
#             "Cadre": 8,
#             "EmployeeType": 9,
#             "EmployeeGrade": 10,
#             "Qualification": 11,
#             "Employee": 12,
#         }

#         app_dict = self._build_app_dict(request)
#         # Sort the apps alphabetically.
#         app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

#         # Sort the models within each app according to the defined ordering
#         for app in app_list:
#             app['models'].sort(key=lambda x: ordering.get(x['name'], float('inf')))

#         return app_list
    

#     # Create an instance of the custom admin site
# custom_admin_site = CustomAdminSite(name='custom_admin')

# # Register your models with the custom admin site
# custom_admin_site.register(Group, GroupAdmin)
# custom_admin_site.register(FunctionalGroup, FunctionalGroupAdmin)
# custom_admin_site.register(Division, DivisionAdmin)
# custom_admin_site.register(Wing, WingAdmin)
# custom_admin_site.register(Region, RegionAdmin)
# custom_admin_site.register(Branch, BranchAdmin)
# custom_admin_site.register(Designation, DesignationAdmin)
# custom_admin_site.register(Cadre, CadreAdmin)
# custom_admin_site.register(EmployeeType, EmployeeTypeAdmin)
# custom_admin_site.register(EmployeeGrade, EmployeeGradeAdmin)
# custom_admin_site.register(Qualification, QualificationAdmin)
# custom_admin_site.register(Employee, EmployeeAdmin)
    



