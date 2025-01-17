from django.contrib import admin
from django.urls import path, include, re_path
from employee_attendance.consumers import LeaveNotificationConsumer

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),

    
    path('', include("HRIS_App.urls")),
    path('', include("reporting.urls")),
    path('', include("account.urls")), 
    path('', include("transfer_employees.urls")),
    path('', include("group_head.urls")),
    path('', include("employee_user.urls")),
    path('', include("employee_attendance.urls")),
]

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', LeaveNotificationConsumer.as_asgi()),
]
