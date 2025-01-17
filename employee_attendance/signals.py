from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import LeaveApplication

@receiver(post_save, sender=LeaveApplication)
def notify_admin_on_leave_application(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "leave_notifications",
            {
                "type": "send_notification",
                "message": {
                    "title": "New Leave Application",
                    "content": f"{instance.employee.name} has applied for leave.",
                },
            },
        )
