

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', include("HRIS_App.urls")),
    path('', include("reporting.urls")),
    path('', include("account.urls")), 
    path('', include("transfer_employees.urls")),
]
