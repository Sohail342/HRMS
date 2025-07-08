from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_view, name='analytics'),
    path('bom-report/', views.bom_report_view, name='bom_report'),
    path('reo-report/', views.reo_report_view, name='reo_report'),
    path('reic-report/', views.reic_report_view, name='reic_report'),
    path('division-wise-report/', views.division_wise_report_view, name='division_wise_report'),
    path('region-wise-report/', views.region_wise_report_view, name='region_wise_report'),
    path('branch-wise-report/', views.branch_wise_report_view, name='branch_wise_report'),
    path('wing-wise-report/', views.wing_wise_report_view, name='wing_wise_report'),
    path('ho-report/', views.ho_report_view, name='ho_report'),
    path('api/regions/', views.api_regions, name='api_regions'),
    path('api/branches/', views.api_branches, name='api_branches'),
]