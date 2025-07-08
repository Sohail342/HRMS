from . import views
from django.urls import path

app_name = "employee_attendance"

urlpatterns = [
    
    path('apply_permanent_leave/', views.apply_permanent_leave, name='apply_permanent_leave'),
    path('stationaryrequests/', views.stationaryrequests, name='stationaryrequests'),
    path('nicrequests/', views.nicrequests, name='nicrequests'),
    path('contractrenewal/', views.contractrenewal, name='contractrenewal'),
    path('upload_education_documents/<int:sap_id>/', views.upload_education_documents, name='upload_education_documents'),

]


