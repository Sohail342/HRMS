from django.urls import path
from .views import InquiryPending, TransferView

app_name = "transfer_employees"

urlpatterns = [
    path('inquiry/<int:SAP_ID>/', InquiryPending.as_view(), name='pending'),
    path('transfer/<int:SAP_ID>/', TransferView.as_view(), name='transfer'),
  
]
