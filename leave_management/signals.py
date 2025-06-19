from django.db.models.signals import post_save
from django.dispatch import receiver
from leave_management.models import LeaveManagement, LeaveBalance
from datetime import datetime

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
                year=year
            )

            if lb.remaining >= leave_days:
                lb.remaining -= leave_days
                lb.save()
            else:
                print(f"Not enough leave balance for {instance.employee.username}")

        except LeaveBalance.DoesNotExist:
            print(f"No leave balance found for {instance.employee.username}")
