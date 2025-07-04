
from django.urls import path
from . import views

app_name = 'HRMS'

urlpatterns = [
    path('', views.index, name="home"),
    path('employees/data/', views.employees_view, name="employees_view"),
    path('download_csv/', views.download_employees_csv, name='download_employees_csv'),
    path('employee/<int:sap_id>/', views.employee_detail_view, name='employee_detail'),
    path('remaining_grades/', views.calculate_remaining_grades, name="remaining_grades"),
    path('assign-grade/', views.assign_grade, name='assign_grade'),
    path('apa-grading/', views.apa_grading_view, name='apa_grading'),
]

