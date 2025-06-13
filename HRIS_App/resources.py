from import_export import resources, fields
from import_export.widgets import DateWidget
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import resources
from import_export.results import RowResult
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
    designation = fields.Field(
        column_name='designation',
        attribute='designation',
        widget=ForeignKeyWidget(Designation, 'title')
    )
    cadre = fields.Field(
        column_name='cadre',
        attribute='cadre',
        widget=ForeignKeyWidget(Cadre, 'name')
    )
    employee_type = fields.Field(
        column_name='employee_type',
        attribute='employee_type',
        widget=ForeignKeyWidget(EmployeeType, 'name')
    )
    employee_grade = fields.Field(
        column_name='employee_grade',
        attribute='employee_grade',
        widget=ForeignKeyWidget(EmployeeGrade, 'grade_name')
    )
    branch = fields.Field(
        column_name='branch',
        attribute='branch',
        widget=ForeignKeyWidget(Branch, 'branch_name')
    )
    region = fields.Field(
        column_name='region',
        attribute='region',
        widget=ForeignKeyWidget(Region, 'name')
    )
    qualifications = fields.Field(
        column_name='qualifications',
        attribute='qualifications',
        widget=ManyToManyWidget(Qualification, separator=',', field='name')
    )
    date_of_joining = fields.Field(
        column_name='date_of_joining',
        attribute='date_of_joining'
    )
    
    birth_date = fields.Field(
        column_name='birth_date',
        attribute='birth_date'
    )
    # Check for other date fields and modify them similarly
    date_of_retirement = fields.Field(
        column_name='date_of_retirement',
        attribute='date_of_retirement'
    )
    
    date_of_contract_expiry = fields.Field(
        column_name='date_of_contract_expiry',
        attribute='date_of_contract_expiry'
    )
    
    date_current_posting = fields.Field(
        column_name='date_current_posting',
        attribute='date_current_posting'
    )
    
    date_current_assignment = fields.Field(
        column_name='date_current_assignment',
        attribute='date_current_assignment'
    )
    
    date_of_last_promotion = fields.Field(
        column_name='date_of_last_promotion',
        attribute='date_of_last_promotion'
    )
    
    # Add a custom import_row method to handle existing CNIC numbers and SAP_ID updates
    def import_row(self, row, instance_loader, **kwargs):
        # First check if we have a SAP_ID in the row
        sap_id = row.get('SAP_ID')
        if sap_id:
            try:
                # Try to find an employee with this SAP_ID
                existing_employee = Employee.objects.get(SAP_ID=sap_id)
                # If found, use the existing instance for update
                row_result = super().import_row(row, instance_loader, **kwargs)
                # Update the instance with the existing employee
                row_result.instance = existing_employee
                return row_result
            except Employee.DoesNotExist:
                # If no employee with this SAP_ID exists, continue with CNIC check
                pass
        
        # If no SAP_ID match, check for CNIC match
        cnic_no = row.get('cnic_no')
        if cnic_no:
            try:
                existing_employee = Employee.objects.get(cnic_no=cnic_no)
                # If found, use the existing instance instead of creating a new one
                row_result = super().import_row(row, instance_loader, **kwargs)
                # Update the instance with the existing employee
                row_result.instance = existing_employee
                return row_result
            except Employee.DoesNotExist:
                # If no existing employee found, proceed with normal import
                pass
        
        # Default import behavior
        return super().import_row(row, instance_loader, **kwargs)

    class Meta:
        model = Employee
        import_id_fields = ('SAP_ID',)
        fields = (
            'id', 'SAP_ID', 'email', 'password', 'name', 'designation', 'cadre', 'employee_type',
            'employee_grade', 'branch', 'region', 'qualifications', 'date_of_joining',
            'mobile_number', 'date_of_last_promotion', 'remarks', 'grade_assignment',
            'date_of_retirement', 'birth_date', 'date_of_contract_expiry', 'date_current_posting',
            'date_current_assignment', 'cnic_no'
        )
        export_order = (
            'SAP_ID', 'email', 'name', 'designation', 'cadre', 'employee_type',
            'employee_grade', 'branch', 'region', 'qualifications',
            'mobile_number', 'date_of_last_promotion', 'remarks', 'grade_assignment',
            'date_of_joining', 'date_of_contract_expiry', 'date_current_posting',
            'date_current_assignment', 'date_of_retirement', 'birth_date', 'cnic_no',
        )

