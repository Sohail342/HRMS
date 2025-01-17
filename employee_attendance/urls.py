from . import views
from django.urls import path

app_name = "employee_attendance"

urlpatterns = [
    # path('contractual_leave_dashboard/', views.contractual_leave_dashboard, name='contractual_leave_dashboard'),
    # path('permanent_leave_dashboard/', views.permanent_leave_dashboard, name='permanent_leave_dashboard'),
    path('apply_permanent_leave/', views.apply_permanent_leave, name='apply_permanent_leave'),
    path('apply_contractual_leave/', views.apply_contractual_leave, name='apply_contractual_leave'),
    path('stationaryrequests/', views.stationaryrequests, name='stationaryrequests'),
    path('nicrequests/', views.nicrequests, name='nicrequests'),
    path('contractrenewal/', views.contractrenewal, name='contractrenewal'),
    path('upload_education_documents/', views.upload_education_documents, name='upload_education_documents'),
    path('leave_management_dashboard/', views.leave_management_dashboard, name='leave_management_dashboard'),
    path('approve/<int:request_id>/<str:status>/', views.status_approval, name='status_approval'),
]


