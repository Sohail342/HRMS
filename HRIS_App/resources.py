from import_export import resources, fields
from import_export.widgets import DateWidget
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import (
Employee, 
Designation, 
Cadre, 
EmployeeType, 
EmployeeGrade, 
Branch, 
Qualification, 
Wing, Region, 
FunctionalGroup, 
Group, Division
)


class WingResource(resources.ModelResource):
    # Map the 'wing_name' to use the 'name' field of Wing
    division_name = fields.Field(
        column_name='division_name',
        attribute='division_name',   
        widget=ForeignKeyWidget(Division, 'division_name')  
    )

    class Meta:
        model = Wing
        fields = ('id', 'name', 'description', 'division_name') 
        export_order = ('name', 'description', 'division_name')
    

class BranchResource(resources.ModelResource):
    # Map the 'branch_region' to use the 'name' field of Region
    region = fields.Field(
        column_name='region',
        attribute='region',   
        widget=ForeignKeyWidget(Region, 'name')  
    )

    class Meta:
        model = Branch
        fields = ('id', 'branch_code', 'branch_name', 'branch_Category', 'branch_address', 'region')
        export_order = ('branch_code', 'branch_name', 'branch_Category', 'branch_address', 'region') 


class FunctionalGroupResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='name') 
    )

    class Meta:
        model = FunctionalGroup
        fields = ('name', 'allias', 'group') 
        export_order = ('name', 'allias', 'group') 



class EmployeeResource(resources.ModelResource):
    
    # Define fields with ForeignKeyWidget for `to_field` foreign key relationships
    designation = fields.Field(
        column_name='designation',
        attribute='designation',
        widget=ForeignKeyWidget(Designation, field='title')
    )
    
    cadre = fields.Field(
        column_name='cadre',
        attribute='cadre',
        widget=ForeignKeyWidget(Cadre, field='name')
    )
    employee_type = fields.Field(
        column_name='employee_type',
        attribute='employee_type',
        widget=ForeignKeyWidget(EmployeeType, field='name')
    )
    employee_grade = fields.Field(
        column_name='employee_grade',
        attribute='employee_grade',
        widget=ForeignKeyWidget(EmployeeGrade, field='grade_name')
    )
    branch = fields.Field(
        column_name='branch',
        attribute='branch',
        widget=ForeignKeyWidget(Branch, field='branch_name')
    )
    region = fields.Field(
        column_name='region',
        attribute='region',
        widget=ForeignKeyWidget(Region, field='name')
    )
    qualifications = fields.Field(
        column_name='qualifications',
        attribute='qualifications',
        widget=ManyToManyWidget(Qualification, separator=',', field='name')
    )

    class Meta:
        model = Employee
        fields = (
            'id', 'SAP_ID', 'email', 'password', 'name', 'designation', 'cadre', 'employee_type',
            'employee_grade', 'branch', 'region', 'qualifications', 'date_of_joining',
            'mobile_number', 'date_of_last_promotion', 'remarks', 'grade_assignment', 'date_of_joining', 
            'date_of_retirement', 'birth_date', 'date_of_contract_expiry', 'date_current_posting', 
            'date_current_assignment'
            
        )
        export_order = (
            'SAP_ID', 'email', 'name', 'designation', 'cadre', 'employee_type',
            'employee_grade', 'branch', 'region', 'qualifications',
            'mobile_number', 'date_of_last_promotion', 'remarks', 'grade_assignment',
            'is_active', 'is_admin', 'is_admin_employee', 'is_letter_template_admin', 
            'created_at', 'updated_at', 'date_of_joining', 'cnic_no', 'husband_or_father_name',
            'date_of_contract_expiry', 'date_current_posting',
            'date_current_assignment', 'date_of_retirement', 'birth_date', 'admin_signature',
            'employee_user'
            
        )
