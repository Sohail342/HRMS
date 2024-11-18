from django.urls import path
from . import views

app_name = 'reporting'


urlpatterns = [
    #  Letter Templates
    path('leave_memorandum/<str:sap_id>/', views.LeaveMemorandum.as_view(), name="leave_memorandum"),
    path('joining_memorandum/<str:sap_id>/', views.JoiningMemorandum.as_view(), name="joining_memorandum"),
    path('order_office_memorandun/<str:sap_id>/', views.OrderOfficeMemorandum.as_view(), name="order_office_memorandun"),
    path('approval_permission_hospitalization/<str:sap_id>/', views.ApprovalPermissionHospitilization.as_view(), name="approval_permission_hospitalization"),
    path('maternity_Leave/<str:sap_id>/', views.MaternityLeaveMemorandum.as_view(), name="maternity_Leave"), 
    path('request_for_issuance/<str:sap_id>/', views.RequestForIssuanceOfficeMemorandum.as_view(), name="request_for_issuance"),
    path('payment_of_bill/<str:sap_id>/', views.PaymentOfBillMemorandum.as_view(), name="payment_of_bill"), 
    path('grant_of_extension/<str:sap_id>/', views.GrantOfExtensionMemorandum.as_view(), name="grant_of_extension"), 
    path('reimbursement/<str:sap_id>/', views.ReimbursementMemorandum.as_view(), name="reimbursement"),  
    path('relieving_order/<str:sap_id>/', views.RelievingOrderMemorandum.as_view(), name="relieving_order"),
    path('permission_of_hospitalization/<str:sap_id>/', views.PermissionOfHospitalization.as_view(), name="permission_of_hospitalization"),
    path('reimbursement_against_purchase/<str:sap_id>/', views.ReimbursementAgainstPurchase.as_view(), name="reimbursement_against_purchase"),


    path('letterform/', views.LetterForm.as_view(), name="lettername"),
    path('get_employee_data/', views.get_employee_data, name='get_employee_data'),
]

