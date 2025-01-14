from . import views
from django.urls import path

app_name = "employee_user"

urlpatterns = [
    path("user/verification/", views.verification_user_view, name="user_verification"), 
    path("user/login/", views.user_login_view, name="user_login"),
    path("user/create_password/<int:sap_id>/", views.create_password_view, name="create_password"),  
    path("user/dashboard/", views.dashboard_view, name="dashboard"),
    path('user/information/form/', views.information_employee, name="employee_information"),
    path('user/ricp/form/', views.RICP, name="ricp_form"),
    path('user/customer_kpi/form/', views.customer_kpi, name="customer_kpi"),
    path('user/financials_kpi/form/', views.financials_kpi, name="financials_kpi"),
    path('user/learning_growth_kpi/form/', views.learning_growth_kpi, name="learning_growth_kpi"),
    path('user/kpi/summary/', views.overall_kpi_result, name="kpi_summary"),
    
    
    # Ajax
    path("submit-ricp-data/", views.submit_form_data, name="submit_ricp_data"),
]
    