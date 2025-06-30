from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import FrozenLeaveBalance, LeaveType
from HRIS_App.models import Employee

class FrozenLeaveBalanceResource(resources.ModelResource):
    employee = fields.Field(
        column_name='employee_SAP_ID', 
        attribute='employee',
        widget=ForeignKeyWidget(Employee, 'SAP_ID')
    )

    leave_type = fields.Field(
        column_name='leave_type__name',
        attribute='leave_type',
        widget=ForeignKeyWidget(LeaveType, 'name')
    )

    class Meta:
        model = FrozenLeaveBalance
        import_id_fields = ('employee', 'leave_type', 'year') 
        fields = (
            'employee',              
            'leave_type',          
            'year',
            'days'
        )
        export_order = (
            'employee',
            'leave_type',
            'year',
            'days'
        )