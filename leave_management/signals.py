from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from leave_management.models import LeaveManagement, LeaveBalance, EmployeeProfile
from leave_management.leave_utils import initialize_leave_balances_for_new_year
from HRIS_App.models import Employee

@receiver(pre_save, sender=LeaveManagement)
def validate_leave_approval(sender, instance, **kwargs):
    # Get the original instance from the database if it exists
    try:
        original = LeaveManagement.objects.get(pk=instance.pk)
        # Only check if status is being changed to 'Approved'
        if original.status != 'Approved' and instance.status == 'Approved':
            year = instance.start_date.year
            leave_days = instance.leave_days

            # Find matching leave balance
            try:
                lb = LeaveBalance.objects.get(
                    employee=instance.employee,
                    leave_type=instance.leave_type,
                    year=year,
                    is_mandatory=False
                )

                # Check if employee has zero balance
                if lb.remaining == 0:
                    raise ValidationError(f"Cannot approve leave: {instance.employee.name} has 0 {instance.leave_type.name} leaves remaining")
                # Check if employee has insufficient balance
                elif lb.remaining < leave_days:
                    raise ValidationError(f"Cannot approve leave: {instance.employee.name} has insufficient {instance.leave_type.name} leave balance ({lb.remaining} remaining, {leave_days} requested)")
                
                # Check mandatory leave balance if this is a mandatory leave
                if instance.is_mandatory and instance.leave_type.name == 'Privileged':
                    # Initialize mandatory leave balance if not set
                    if lb.mandatory_annual_quota == 0:
                        lb.mandatory_annual_quota = 15  # Set to 15 days as per requirement
                        lb.mandatory_remaining = min(15, lb.remaining)  # Set to min of 15 or remaining balance
                        lb.save()
                    
                    # Check if mandatory leave balance is sufficient
                    if lb.mandatory_remaining < leave_days:
                        raise ValidationError(f"Cannot approve leave: {instance.employee.name} has insufficient mandatory {instance.leave_type.name} leave balance ({lb.mandatory_remaining} remaining, {leave_days} requested)")

            except LeaveBalance.DoesNotExist:
                raise ValidationError(f"Cannot approve leave: No leave balance found for {instance.employee.name}")
            except LeaveBalance.MultipleObjectsReturned:
                # Handle the case where multiple leave balances exist
                lb = LeaveBalance.objects.filter(
                    employee=instance.employee,
                    leave_type=instance.leave_type,
                    year=year,
                    is_mandatory=False
                ).first()
                if not lb:
                    raise ValidationError(f"Cannot approve leave: No leave balance found for {instance.employee.name}")
                
                # Continue with the same validation as above
                if lb.remaining == 0:
                    raise ValidationError(f"Cannot approve leave: {instance.employee.name} has 0 {instance.leave_type.name} leaves remaining")
                elif lb.remaining < leave_days:
                    raise ValidationError(f"Cannot approve leave: {instance.employee.name} has insufficient {instance.leave_type.name} leave balance ({lb.remaining} remaining, {leave_days} requested)")
                
                # Check mandatory leave balance if this is a mandatory leave
                if instance.is_mandatory and instance.leave_type.name == 'Privileged':
                    # Initialize mandatory leave balance if not set
                    if lb.mandatory_annual_quota == 0:
                        lb.mandatory_annual_quota = 15  # Set to 15 days as per requirement
                        lb.mandatory_remaining = min(15, lb.remaining)  # Set to min of 15 or remaining balance
                        lb.save()
                    
                    # Check if mandatory leave balance is sufficient
                    if lb.mandatory_remaining < leave_days:
                        raise ValidationError(f"Cannot approve leave: {instance.employee.name} has insufficient mandatory {instance.leave_type.name} leave balance ({lb.mandatory_remaining} remaining, {leave_days} requested)")
    except LeaveManagement.DoesNotExist:
        # This is a new instance being created, no validation needed
        pass

@receiver(post_save, sender=LeaveManagement)
def deduct_leave_on_approval(sender, instance, **kwargs):
    if instance.status == 'Approved':
        year = instance.start_date.year
        leave_days = instance.leave_days

        # Find matching leave balance
        try:
            lb = LeaveBalance.objects.get(
                employee=instance.employee,
                leave_type=instance.leave_type,
                year=year,
                is_mandatory=False
            )

            # Deduct the leave days if sufficient balance
            # (We've already validated the balance in pre_save)
            lb.remaining -= leave_days
            
            # If this is a mandatory leave, also deduct from mandatory balance
            if instance.is_mandatory and instance.leave_type.name == 'Privileged':
                # Initialize mandatory leave balance if not set
                if lb.mandatory_annual_quota == 0:
                    lb.mandatory_annual_quota = 15  # Set to 15 days as per requirement
                    lb.mandatory_remaining = min(15, lb.remaining + leave_days)  # Set to min of 15 or original remaining balance
                
                # Deduct from mandatory balance
                lb.mandatory_remaining -= leave_days
            
            lb.save()

        except LeaveBalance.DoesNotExist:
            # This shouldn't happen due to pre_save validation
            pass
        except LeaveBalance.MultipleObjectsReturned:
            # Handle the case where multiple leave balances exist
            lb = LeaveBalance.objects.filter(
                employee=instance.employee,
                leave_type=instance.leave_type,
                year=year,
                is_mandatory=False
            ).first()
            
            if lb:
                # Deduct the leave days if sufficient balance
                lb.remaining -= leave_days
                
                # If this is a mandatory leave, also deduct from mandatory balance
                if instance.is_mandatory and instance.leave_type.name == 'Privileged':
                    # Initialize mandatory leave balance if not set
                    if lb.mandatory_annual_quota == 0:
                        lb.mandatory_annual_quota = 15  # Set to 15 days as per requirement
                        lb.mandatory_remaining = min(15, lb.remaining + leave_days)  # Set to min of 15 or original remaining balance
                    
                    # Deduct from mandatory balance
                    lb.mandatory_remaining -= leave_days
                
                lb.save()


# @receiver(post_save, sender=Employee)
# def create_employee_profile(sender, instance, created, **kwargs):
#     """
#     Create an EmployeeProfile when a new Employee is created.
#     Uses related EmployeeType and Cadre if available.
#     """
#     if created:
#         if hasattr(instance, 'employeeprofile'):
#             return  # Avoid duplicates

#         # Extract names from related foreign keys safely
#         cadre = instance.cadre.name if instance.cadre else "Officer"
#         emp_type = instance.employee_type.name if instance.employee_type else "Regular"

#         EmployeeProfile.objects.create(
#             employee=instance,
#             cadre=cadre,
#             employment_type=emp_type,
#             contract_start_date=(
#                 timezone.now().date()
#                 if emp_type == "Contractual"
#                 else None
#             )
#         )


# @receiver(post_save, sender=EmployeeProfile)
# def initialize_leave_balances(sender, instance, created, **kwargs):
#     """
#     Initialize leave balances for a new employee profile.
#     """
#     if created:
#         # Initialize leave balances for the current year
#         current_year = timezone.now().year
#         initialize_leave_balances_for_new_year(current_year)
