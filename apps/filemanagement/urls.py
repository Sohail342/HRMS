from django.urls import path
from . import views

app_name = 'filemanagement'

urlpatterns = [
    path('', views.file_management_dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('preview/<int:file_id>/', views.preview_file, name='preview_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('send/<int:file_id>/', views.send_file, name='send_file'),
]