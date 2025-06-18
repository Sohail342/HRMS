from . import views
from django.urls import path
from . import views_leave_management

app_name = "employee_attendance"

urlpatterns = [
    
    path('apply_permanent_leave/', views.apply_permanent_leave, name='apply_permanent_leave'),
    path('stationaryrequests/', views.stationaryrequests, name='stationaryrequests'),
    path('nicrequests/', views.nicrequests, name='nicrequests'),
    path('contractrenewal/', views.contractrenewal, name='contractrenewal'),
    path('upload_education_documents/<int:sap_id>/', views.upload_education_documents, name='upload_education_documents'),
    path('leave_management_dashboard/', views.leave_management_dashboard, name='leave_management_dashboard'),
    path('approve/<int:request_id>/<str:leave_status>/', views.status_approval, name='status_approval'),
    path('adjust_leave_balance/', views_leave_management.adjust_leave_balance, name='adjust_leave_balance'),
    path('apply_leave/', views_leave_management.apply_leave, name='apply_leave'),
    path('view_leave_history/', views_leave_management.view_leave_history, name='view_leave_history'),
    path('view_leave_balances/', views_leave_management.view_leave_balances, name='view_leave_balances'),
    path('process_year_end/', views_leave_management.process_year_end, name='process_year_end'),
    path('leave_policy_management/', views_leave_management.leave_policy_management, name='leave_policy_management'),
    path('add_leave_type/', views_leave_management.add_leave_type, name='add_leave_type'),
    path('add_leave_policy/', views_leave_management.add_leave_policy, name='add_leave_policy'),
]


