from django.urls import path
from . import views

urlpatterns = [
    path('teacher/', views.teacher_assignments, name='teacher_assignments'),
    path('student/', views.student_assignments, name='student_assignments'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('submissions/<int:assignment_id>/', views.view_submissions, name='view_submissions'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
]
