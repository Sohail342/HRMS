from django.urls import path
from .import views


app_name = 'group_head'
urlpatterns = [
    path('grade_distribution/', views.grade_distribution_view, name='grade_distribution_view'), 
    path('grade_distribution_branch/<str:region_name>/', views.grade_distribution_region_view, name='grade_distribution_branch_view'),
    path('assign-grades/', views.assign_grade, name='assign-grades'),
]
