from django.db import models
from apps.HRIS_App.models import Employee

class Inquiry(models.Model):
    admin_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='inquiries')
    transferred_employee = models.CharField(max_length=200, default='', blank=True, null=True) 
    transfer_remarks = models.TextField(blank=True, null=True)
    transferred_status = models.CharField(
        max_length=20,
        choices=[('within_group', 'Transferred Within Group'), ('outside_group', 'Transferred Outside Group')],
        default='within_group'
    )
    admin_action = models.CharField(
        max_length=100, 
        choices=[('close', 'close'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default=" "
    )
    action_taken_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inquiry for {self.admin_employee} - Status: {self.admin_action}"
    

    def save(self, *args, **kwargs):
        if self.admin_action in ["close"]:
            # If the admin approves or rejects, delete the inquiry
            super(Inquiry, self).delete()
            return  # Prevents the inquiry from being saved (because it's deleted)
        
        super(Inquiry, self).save(*args, **kwargs)  

    class Meta:
        verbose_name = "Transfer Inquiry"
        verbose_name_plural = "Transfer Inquiries"
