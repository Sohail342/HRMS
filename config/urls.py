from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include("apps.HRIS_App.urls")),
    path('', include("apps.reporting.urls")),
    path('', include("apps.account.urls")), 
    path('', include("apps.transfer_employees.urls")),
    path('', include("apps.group_head.urls")),
    path('', include("apps.employee_user.urls")),
    path('', include("apps.employee_attendance.urls")),
    path('employee-search/', include("apps.employee_search.urls")),
    path('', include("apps.leave_management.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path('files/', include("apps.filemanagement.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

