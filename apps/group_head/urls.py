from django.urls import path
from .import views


app_name = 'group_head'
urlpatterns = [
    path('grade_distribution/', views.grade_distribution_view, name='grade_distribution_view'), 
    path('grade_distribution/branch/<str:region_name>/', views.grade_distribution_region_view, name='grade_distribution_branch_view'),
    path('assign-grades/', views.assign_grade, name='assign-grades'), 
    path('uploaded/csv_files/', views.uploaded_csv_files, name='uploaded_csv_files'),
    path('upload_Assigned_grades/<str:region_id>/', views.AssignedGradesByBranchesView, name='upload_Assigned_grades'),

    path('search/employee/', views.SearchEmployee.as_view(), name="employee_search"),
    path('employee/<int:sap_id>/upload_pdf/', views.UploadBSCFrom.as_view(), name='upload_pdf'),
]
