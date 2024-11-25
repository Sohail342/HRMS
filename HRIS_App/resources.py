from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import Employee, Designation, Cadre, EmployeeType, EmployeeGrade, Branch, Qualification, Region, FunctionalGroup, Group

class BranchResource(resources.ModelResource):
    # Map the 'branch_region' to use the 'name' field of Region
    branch_region = fields.Field(
        column_name='region',  # CSV column name
        attribute='region',   # Model field
        widget=ForeignKeyWidget(Region, 'name')  # Match using Region's 'region_id' field
    )

    class Meta:
        model = Branch
        fields = ('branch_code', 'branch_name', 'branch_Category', 'branch_address', 'region')  # Fields to import/export
        import_id_fields = ('branch_code',)  # Unique field for identifying rows during import


class FunctionalGroupResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='name')  # Referencing the Group model's name field
    )

    class Meta:
        model = FunctionalGroup
        fields = ('id', 'name', 'allias', 'group')  # Fields to include in import/export
        export_order = ('id', 'name', 'allias', 'group')  # Order of fields in the exported file


class RegionResource(resources.ModelResource):
    functional_group = fields.Field(
        column_name='functional_group',
        attribute='functional_group',
        widget=ManyToManyWidget(FunctionalGroup, separator=',', field='name')  # Handles ManyToManyField using 'name'
    )

    class Meta:
        model = Region
        fields = ('id', 'name', 'region_category', 'functional_group')  # Fields to include
        export_order = ('id', 'name', 'region_category', 'functional_group')  # Export field order


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
        widget=ForeignKeyWidget(Cadre, field='name')  # Adjust the field name based on your Cadre model
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
        widget=ForeignKeyWidget(Branch, field='branch_code')
    )
    region = fields.Field(
        column_name='region',
        attribute='region',
        widget=ForeignKeyWidget(Region, field='name')  # Adjust the field name based on Region's model
    )
    qualifications = fields.Field(
        column_name='qualifications',
        attribute='qualifications',
        widget=ManyToManyWidget(Qualification, separator=',', field='name')
    )

    class Meta:
        model = Employee
        fields = (
            'id', 'email', 'name', 'designation', 'cadre', 'employee_type',
            'employee_grade', 'branch', 'region', 'qualifications', 'date_of_joining',
            'mobile_number', 'date_of_last_promotion', 'remarks', 'grade_assignment',
        )
        export_order = (
            'id', 'email', 'name', 'designation', 'cadre', 'employee_type',
            'employee_grade', 'branch', 'region', 'qualifications', 'date_of_joining',
            'mobile_number', 'date_of_last_promotion', 'remarks', 'grade_assignment',
        )
