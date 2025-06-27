from django.urls import path
from . import views

app_name = 'reporting'


urlpatterns = [
    #  Letter Templates
    path('leave_memorandum/', views.LeaveMemorandum.as_view(), name="leave_memorandum"),
    path('privilege_leave_memorandum/', views.PrivilegeLeaveMemorandum.as_view(), name="privilege_leave_memorandum"),
    path('hospitalization/', views.Hospitilization.as_view(), name="hospitalization"),
    path('request_for_issuance/<str:sap_id>/', views.RequestForIssuanceOfficeMemorandum.as_view(), name="request_for_issuance"),
    


    path('letterform/', views.LetterForm.as_view(), name="lettername"),
    path('get_employee_data/', views.get_employee_data, name='get_employee_data'), 
    path('get_employee/', views.get_employee, name='get_employee'), 
    path('get_family_member/', views.get_family_member, name='get_family_member'),
    path('save_family_member/', views.save_family_member, name='save_family_member'),
    path('save_pdf_to_cloudinary/', views.save_pdf_to_cloudinary, name='save_pdf_to_cloudinary'),
    path('template_search/', views.template_search, name='template_search'), 
    path('search_permanent_saved_templates', views.search_permanent_saved_templates, name='search_permanent_saved_templates'),
    path('get_letter_templates/', views.get_letter_templates, name='get_letter_templates'),
    path('application_leave/<str:sap_id>/', views.application_leave, name="application_leave"),
    path('save_purpose/', views.save_purpose, name='save_purpose'),
    path('save_hospital/', views.save_hospital, name='save_hospital'),
]

