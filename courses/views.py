from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Timetable, Subject
from django.contrib import messages

@login_required
def timetable_view(request):
    user = request.user
    
    if user.role == 'student':
        if not hasattr(user, 'student_profile'):
            messages.warning(request, "Please complete your profile first.")
            return redirect('complete_profile')
        student = user.student_profile
        # Filter timetable by department and semester
        timetable_entries = Timetable.objects.filter(
            subject__department=student.department,
            subject__semester=student.semester
        ).order_by('day', 'start_time')
        
    elif user.role == 'teacher':
        if not hasattr(user, 'teacher_profile'):
            messages.warning(request, "Please complete your profile first.")
            return redirect('complete_profile')
        teacher = user.teacher_profile
        # Filter timetable by teacher
        timetable_entries = Timetable.objects.filter(
            subject__teacher=teacher
        ).order_by('day', 'start_time')
        
    else:
        # Admin or general staff see all
        timetable_entries = Timetable.objects.all().order_by('day', 'start_time')
        
    # Group by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    grouped_timetable = {day: [] for day in days}
    for entry in timetable_entries:
        if entry.day in grouped_timetable:
            grouped_timetable[entry.day].append(entry)
            
    return render(request, 'courses/timetable.html', {
        'grouped_timetable': grouped_timetable,
        'days': days
    })
