# leave_utils.py
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

from .models import (
    LeaveType, LeaveRule, LeaveBalance, EmployeeProfile,
    FrozenLeaveBalance, LeaveManagement
)


def assign_all_employee_leave_balances():
    current_year = datetime.now().year
    profiles = EmployeeProfile.objects.select_related("employee")

    for profile in profiles:
        rules = LeaveRule.objects.filter(
            cadre=profile.cadre,
            employment_type=profile.employment_type
        )

        for rule in rules:
            LeaveBalance.objects.update_or_create(
                employee=profile.employee,
                leave_type=rule.leave_type,
                year=current_year,
                defaults={
                    "annual_quota": rule.annual_quota,
                    "remaining": rule.annual_quota,
                }
            )


def get_leave_cycle(employee_profile: EmployeeProfile):
    today = date.today()
    if employee_profile.employment_type == "Contractual" and employee_profile.contract_start_date:
        start = employee_profile.contract_start_date
        end = start + relativedelta(years=1)
    elif employee_profile.cadre == "Executive":
        start = date(today.year, 1, 1)
        end = date(today.year + 1, 3, 31)
    else:
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
    return (start, end)


def assign_leave_balances(employee_profile: EmployeeProfile):
    rule_set = LeaveRule.objects.filter(
        cadre=employee_profile.cadre,
        employment_type=employee_profile.employment_type
    )
    for rule in rule_set:
        LeaveBalance.objects.update_or_create(
            employee=employee_profile.employee,
            leave_type=rule.leave_type,
            defaults={"annual_quota": rule.annual_quota, "remaining": rule.annual_quota}
        )


def validate_leave_application(employee, leave_type, start_date, end_date):
    profile = employee.employeeprofile
    cycle_start, cycle_end = get_leave_cycle(profile)
    if start_date < cycle_start or end_date > cycle_end + timedelta(days=30):
        raise ValidationError("Leave dates must fall within your leave cycle.")

    try:
        leave_balance = LeaveBalance.objects.get(employee=employee, leave_type=leave_type)
    except LeaveBalance.DoesNotExist:
        raise ValidationError("Leave balance not set for this type.")

    requested_days = (end_date - start_date).days + 1
    if leave_balance.remaining < requested_days:
        raise ValidationError("Insufficient leave balance.")


def apply_for_leave(employee, leave_type, start_date, end_date, reason):
    validate_leave_application(employee, leave_type, start_date, end_date)

    leave = LeaveManagement.objects.create(
        employee=employee,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status='Pending'
    )
    return leave


def freeze_sick_leaves():
    current_year = datetime.now().year
    sick_leave = LeaveType.objects.get(name="Sick")

    profiles = EmployeeProfile.objects.filter(employment_type="Regular")
    for profile in profiles:
        try:
            lb = LeaveBalance.objects.get(employee=profile.employee, leave_type=sick_leave)
            if lb.remaining > 0 and sick_leave.is_freezable:
                FrozenLeaveBalance.objects.create(
                    employee=profile.employee,
                    leave_type=sick_leave,
                    year=current_year,
                    days=lb.remaining
                )
                lb.remaining = 0
                lb.save()
        except LeaveBalance.DoesNotExist:
            continue


def expire_privileged_leaves():
    privileged = LeaveType.objects.get(name="Privileged")
    today = date.today()
    if today > date(today.year, 3, 31):
        for profile in EmployeeProfile.objects.filter(employment_type="Regular"):
            LeaveBalance.objects.filter(
                employee=profile.employee,
                leave_type=privileged
            ).update(remaining=0)


def is_eligible_for_encashment(employee):
    profile = employee.employeeprofile
    if profile.cadre != "Officer" or profile.employment_type != "Regular":
        return False

    privileged = LeaveType.objects.get(name="Privileged")
    leaves = LeaveManagement.objects.filter(
        employee=employee,
        leave_type=privileged,
        status="Approved",
        start_date__year=datetime.now().year
    )

    total_days = sum([(leave.end_date - leave.start_date).days + 1 for leave in leaves])
    return total_days >= 15
