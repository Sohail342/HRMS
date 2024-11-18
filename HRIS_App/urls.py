
from django.urls import path
from . import views

app_name = 'HRMS'

urlpatterns = [
    path('', views.index, name="home"),
    path('employee/', views.employees_view, name="employees_view"),
    path('download_csv/', views.download_employees_csv, name='download_employees_csv'),
    path('employee/<int:sap_id>/', views.employee_detail_view, name='employee_detail'),
]

