
from django.urls import path
from . import views
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import views as auth_views

app_name = 'account'

success_url = reverse_lazy('account:password_change_done')  

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),


    
    # Password change view
    path('password_change/', 
         PasswordChangeView.as_view(
             template_name='account/password_change_form.html', 
             success_url=success_url
         ), 
         name='password_change'),

     path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name='password_change_done'),
 
]

