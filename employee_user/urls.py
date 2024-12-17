from . import views
from django.urls import path

app_name = "employee_user"

urlpatterns = [
    path("user/verification/", views.verification_user_view, name="user_verification"), 
    path("user/login/", views.user_login_view, name="user_login"),
    path("user/create_password/<int:sap_id>/", views.create_password_view, name="create_password"),  
    path("user/dashboard/", views.dashboard_view, name="dashboard"),
]
    