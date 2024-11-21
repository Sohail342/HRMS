from django.urls import path
from .views import InquiryPending

app_name = "transfer_employees"

urlpatterns = [
    path('transfer/<int:SAP_ID>/', InquiryPending.as_view(), name='transfer'),
  
]
