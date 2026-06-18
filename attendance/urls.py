from django.urls import path
from . import views

urlpatterns = [
    path('student-report/', views.student_attendance, name='student_attendance'),
    path('teacher-dashboard/', views.teacher_attendance_dashboard, name='teacher_attendance_dashboard'),
    path('mark-manual/<int:subject_id>/', views.mark_attendance, name='mark_attendance'),
    path('generate-qr/<int:subject_id>/', views.generate_qr_session, name='generate_qr_session'),
    path('scan/', views.scan_qr_attendance, name='scan_qr_attendance'),
]
