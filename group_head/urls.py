from django.urls import path
from .import views

urlpatterns = [
    path('grade_distribution/', views.grade_distribution_view, name='grade_distribution_view')
]
