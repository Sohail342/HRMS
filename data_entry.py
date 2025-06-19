from HRIS_App.models import Employee
from leave_management.models import EmployeeProfile
from datetime import date

for emp in Employee.objects.all():
    EmployeeProfile.objects.get_or_create(
        employee=emp,
        defaults={
            'cadre': 'Officer',  # Default: adjust if needed
            'employment_type': 'Regular',  # Or 'Contractual'
            'contract_start_date': date(2024, 1, 1)  # Only used for Contractual
        }
    )
