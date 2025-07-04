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
    path('user/update/<str:form_type>/', views.update_kpis, name="update_kpis"),
    path('user/kpi/delete/<int:kpi_id>/<str:form_type>/', views.delete_kpi, name="delete_kpi"),
    
    # Admin employee management
    path('employees/', views.employee_list, name="employee_list"),
    path('employees/delete/<int:employee_id>/', views.delete_employee, name="delete_employee"),
    path('employees/deleted/', views.deleted_employees, name="deleted_employees"),
    path('employees/deleted/details/', views.deleted_employee_details, name="deleted_employee_details"),
    
    # Ajax
    path("submit-ricp-data/", views.submit_form_data, name="submit_ricp_data"),
]
    