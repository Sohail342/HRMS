from django.urls import path
from . import views

app_name = 'leave_management'

urlpatterns = [
    path('get_leave_balances/', views.get_leave_balances, name='get_leave_balances'),
    path('leave-balance/', views.admin_leave_balance, name='leave_balance'),
]