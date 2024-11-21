from datetime import timezone
from django.contrib import admin
from .models import Inquiry
from unfold.admin import ModelAdmin
from .forms import InquiryActionForm
from django.utils.translation import gettext_lazy as _

class InquiryAdmin(ModelAdmin):
    # Define the fields to be displayed in the admin panel
    list_display = ('admin_employee', 'transferred_employee', 'pending_inquiry', 'transferred_status', 'admin_action', 'action_taken_on')
    list_filter = ('pending_inquiry', 'admin_action', 'transferred_status')
    search_fields = ('admin_employee__name', 'remarks')
    
    # Add form customization for admin action and remarks fields
    form = InquiryActionForm

    # Customize fieldsets for better organization in the form
    fieldsets = (
        (None, {
            'fields': ('admin_employee', 'transferred_employee', 'pending_inquiry', 'remarks', 'transferred_status')
        }),
        (_('Admin Action'), {
            'fields': ('admin_action',),
            'classes': ('collapse',) 
        }),
    )

    # Make sure that the remarks field is optional in the admin form
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.admin_action != 'pending':  # Optionally, make remarks readonly after action is taken
            return ['remarks', 'admin_action']
        return []

    # Optional: Update the action_taken_on timestamp whenever admin action is updated
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('admin_action') != obj.admin_action:
            obj.action_taken_on = timezone.now()
        super().save_model(request, obj, form, change)

# Register the model with the admin interface
admin.site.register(Inquiry, InquiryAdmin)
