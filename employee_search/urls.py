from django.urls import path
from . import views

app_name = 'employee_search'

urlpatterns = [
    path('', views.advanced_search, name='advanced_search'),
    path('filter-counts/', views.get_filter_counts, name='get_filter_counts'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('branches-by-region/', views.get_branches_by_region, name='get_branches_by_region'),
]