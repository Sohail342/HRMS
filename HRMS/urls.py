from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),

    
    path('', include("HRIS_App.urls")),
    path('', include("reporting.urls")),
    path('', include("account.urls")), 
    path('', include("transfer_employees.urls")),
    path('', include("group_head.urls")),
    path('', include("employee_user.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
