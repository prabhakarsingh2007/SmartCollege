from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notes
from courses.models import Subject
from students.models import Student
from teachers.models import Teacher

@login_required
def notes_list(request):
    user = request.user
    
    if user.role == 'student':
        if not hasattr(user, 'student_profile'):
            messages.warning(request, "Please complete your profile first.")
            return redirect('complete_profile')
        student = user.student_profile
        # Fetch notes matching student's department and semester
        notes = Notes.objects.filter(
            subject__department=student.department,
            subject__semester=student.semester
        ).order_by('-upload_date')
        subjects = None
        
    elif user.role == 'teacher':
        if not hasattr(user, 'teacher_profile'):
            messages.warning(request, "Please complete your profile first.")
            return redirect('complete_profile')
        teacher = user.teacher_profile
        # Fetch notes uploaded by the teacher
        notes = Notes.objects.filter(teacher=teacher).order_by('-upload_date')
        # Fetch teacher's subjects for upload form dropdown
        subjects = Subject.objects.filter(teacher=teacher)
        
    else:
        notes = Notes.objects.all().order_by('-upload_date')
        subjects = None
        
    if request.method == 'POST' and user.role == 'teacher':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        uploaded_file = request.FILES.get('file')
        
        if title and subject_id and uploaded_file:
            subject = get_object_or_404(Subject, id=subject_id, teacher__user=user)
            Notes.objects.create(
                title=title,
                subject=subject,
                teacher=user.teacher_profile,
                file=uploaded_file
            )
            messages.success(request, f"Notes '{title}' successfully uploaded!")
            return redirect('notes_list')
        else:
            messages.error(request, "Please fill out all fields and upload a file.")
            
    return render(request, 'notes/notes_list.html', {
        'notes': notes,
        'subjects': subjects
    })

@login_required
def delete_notes(request, note_id):
    user = request.user
    if user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    note = get_object_or_404(Notes, id=note_id, teacher__user=user)
    note_title = note.title
    note.file.delete()  # Clean file from storage
    note.delete()
    messages.success(request, f"Notes '{note_title}' deleted successfully.")
    return redirect('notes_list')
