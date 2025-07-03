from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_view, name='analytics'),
    path('bom-report/', views.bom_report_view, name='bom_report'),
    path('api/regions/', views.api_regions, name='api_regions'),
    path('api/branches/', views.api_branches, name='api_branches'),
]