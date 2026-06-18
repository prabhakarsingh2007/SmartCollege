from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Attendance, QRSession
from courses.models import Subject
from students.models import Student
from django.urls import reverse
import qrcode
import io
import base64

@login_required
def student_attendance(request):
    user = request.user
    if user.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    student = get_object_or_404(Student, user=user)
    subjects = Subject.objects.filter(department=student.department, semester=student.semester)
    
    # Calculate attendance per subject
    attendance_report = []
    for subject in subjects:
        total = Attendance.objects.filter(student=student, subject=subject).count()
        present = Attendance.objects.filter(student=student, subject=subject, status='Present').count()
        pct = round((present / total * 100), 1) if total > 0 else 0
        attendance_report.append({
            'subject': subject,
            'total': total,
            'present': present,
            'absent': total - present,
            'percentage': pct
        })
        
    return render(request, 'attendance/student_report.html', {
        'attendance_report': attendance_report
    })

@login_required
def teacher_attendance_dashboard(request):
    user = request.user
    if user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    subjects = Subject.objects.filter(teacher__user=user)
    return render(request, 'attendance/teacher_dashboard.html', {
        'subjects': subjects
    })

@login_required
def mark_attendance(request, subject_id):
    user = request.user
    if user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    subject = get_object_or_404(Subject, id=subject_id, teacher__user=user)
    students = Student.objects.filter(department=subject.department, semester=subject.semester)
    
    selected_date = request.GET.get('date', timezone.now().date().isoformat())
    
    # Check if attendance already marked
    existing_attendance = Attendance.objects.filter(subject=subject, date=selected_date)
    marked_student_ids = {a.student.id: a.status for a in existing_attendance}
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        if not date_str:
            date_str = selected_date
            
        for student in students:
            status = request.POST.get(f'student_{student.id}', 'Absent')
            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=date_str,
                defaults={'status': status}
            )
        messages.success(request, f"Attendance successfully marked for {date_str}!")
        return redirect('teacher_attendance_dashboard')
        
    return render(request, 'attendance/mark_manual.html', {
        'subject': subject,
        'students': students,
        'selected_date': selected_date,
        'marked_student_ids': marked_student_ids
    })

@login_required
def generate_qr_session(request, subject_id):
    user = request.user
    if user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    subject = get_object_or_404(Subject, id=subject_id, teacher__user=user)
    
    # Deactivate existing sessions for this subject
    QRSession.objects.filter(subject=subject, is_active=True).update(is_active=False)
    
    # Create new QR Session expiring in 5 minutes
    expires = timezone.now() + timezone.timedelta(minutes=5)
    session = QRSession.objects.create(
        subject=subject,
        teacher=user.teacher_profile,
        expires_at=expires
    )
    
    # Construct base64 QR code image containing token
    qr_data = session.token.hex
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return render(request, 'attendance/qr_code_display.html', {
        'session': session,
        'qr_base64': qr_base64,
        'expires': expires.isoformat()
    })

@login_required
def scan_qr_attendance(request):
    user = request.user
    if user.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    student = user.student_profile
    
    if request.method == 'POST':
        token_str = request.POST.get('qr_token', '').strip()
        try:
            session = QRSession.objects.get(token=token_str, is_active=True)
            # Check expiration
            if timezone.now() > session.expires_at:
                session.is_active = False
                session.save()
                messages.error(request, "This QR code session has expired.")
                return redirect('student_attendance')
                
            # Verify student belongs to this subject's department/semester
            if session.subject.department != student.department or session.subject.semester != student.semester:
                messages.error(request, "You are not enrolled in this class's department/semester.")
                return redirect('student_attendance')
                
            # Mark attendance
            Attendance.objects.update_or_create(
                student=student,
                subject=session.subject,
                date=timezone.now().date(),
                defaults={'status': 'Present'}
            )
            messages.success(request, f"Attendance marked as PRESENT for {session.subject.name}!")
            return redirect('student_attendance')
            
        except (QRSession.DoesNotExist, ValueError):
            messages.error(request, "Invalid or expired QR token code.")
            
    return render(request, 'attendance/scan_qr.html')
