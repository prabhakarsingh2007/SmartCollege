from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from courses.models import Subject
from students.models import Student
from teachers.models import Teacher

@login_required
def teacher_assignments(request):
    user = request.user
    if user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    teacher = user.teacher_profile
    assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
    subjects = Subject.objects.filter(teacher=teacher)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject_id = request.POST.get('subject')
        deadline = request.POST.get('deadline')
        attachment = request.FILES.get('file')
        
        if title and description and subject_id and deadline:
            subject = get_object_or_404(Subject, id=subject_id, teacher=teacher)
            Assignment.objects.create(
                title=title,
                description=description,
                subject=subject,
                teacher=teacher,
                deadline=deadline,
                file=attachment
            )
            messages.success(request, f"Assignment '{title}' posted successfully!")
            return redirect('teacher_assignments')
        else:
            messages.error(request, "Please fill out all required fields.")
            
    return render(request, 'assignments/teacher_list.html', {
        'assignments': assignments,
        'subjects': subjects
    })

@login_required
def student_assignments(request):
    user = request.user
    if user.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    student = user.student_profile
    assignments = Assignment.objects.filter(
        subject__department=student.department,
        subject__semester=student.semester
    ).order_by('-created_at')
    
    # Annotate submissions
    for assignment in assignments:
        assignment.user_submission = Submission.objects.filter(assignment=assignment, student=student).first()
        assignment.is_past_deadline = timezone.now() > assignment.deadline
        
    return render(request, 'assignments/student_list.html', {
        'assignments': assignments
    })

@login_required
def submit_assignment(request, assignment_id):
    user = request.user
    if user.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    student = user.student_profile
    assignment = get_object_or_404(Assignment, id=assignment_id, subject__department=student.department, subject__semester=student.semester)
    
    if timezone.now() > assignment.deadline:
        messages.error(request, "Cannot submit. The deadline has passed.")
        return redirect('student_assignments')
        
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            Submission.objects.update_or_create(
                assignment=assignment,
                student=student,
                defaults={
                    'file': uploaded_file,
                    'submitted_at': timezone.now(),
                    'status': 'Submitted'
                }
            )
            messages.success(request, f"Successfully submitted assignment for '{assignment.title}'!")
            return redirect('student_assignments')
        else:
            messages.error(request, "Please attach a file before submitting.")
            
    return render(request, 'assignments/submit.html', {'assignment': assignment})

@login_required
def view_submissions(request, assignment_id):
    user = request.user
    if user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher__user=user)
    submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    return render(request, 'assignments/submissions_list.html', {
        'assignment': assignment,
        'submissions': submissions
    })

@login_required
def grade_submission(request, submission_id):
    user = request.user
    if user.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    submission = get_object_or_404(Submission, id=submission_id, assignment__teacher__user=user)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        
        if grade:
            submission.grade = grade
            submission.feedback = feedback
            submission.status = 'Graded'
            submission.save()
            messages.success(request, f"Graded successfully for student {submission.student.user.username}.")
            return redirect('view_submissions', assignment_id=submission.assignment.id)
        else:
            messages.error(request, "Please enter a valid grade.")
            
    return render(request, 'assignments/grade.html', {'submission': submission})
