from django.contrib import admin
from .models import Inquiry
from unfold.admin import ModelAdmin

class InquiryAdmin(ModelAdmin):
    # Define the fields to be displayed in the admin panel
    list_display = ('admin_employee', 'transferred_employee', 'transferred_status', 'admin_action', 'action_taken_on')
    list_filter = ('admin_action', 'transferred_status')
    search_fields = ('admin_employee__name', 'remarks')
    

# Register the model with the admin interface
admin.site.register(Inquiry, InquiryAdmin)
