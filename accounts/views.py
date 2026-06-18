from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, StudentProfileForm, TeacherProfileForm
from students.models import Student
from teachers.models import Teacher
from courses.models import Department, Subject, Timetable
from notices.models import Notice
from assignments.models import Assignment, Submission
from attendance.models import Attendance

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            messages.success(request, f"Account created for {user.username}! Please log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('login')
    return redirect('dashboard')

@login_required
def complete_profile(request):
    user = request.user
    
    # Check if profile already exists
    if user.role == 'student' and hasattr(user, 'student_profile'):
        return redirect('dashboard')
    elif user.role == 'teacher' and hasattr(user, 'teacher_profile'):
        return redirect('dashboard')
    elif user.role == 'admin':
        return redirect('dashboard')
        
    if user.role == 'student':
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                messages.success(request, "Your student profile is complete!")
                return redirect('dashboard')
        else:
            form = StudentProfileForm()
        role_title = "Student"
    else: # teacher
        if request.method == 'POST':
            form = TeacherProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                messages.success(request, "Your teacher profile is complete!")
                return redirect('dashboard')
        else:
            form = TeacherProfileForm()
        role_title = "Teacher"
        
    # Check if any departments exist
    departments_exist = Department.objects.exists()
    
    return render(request, 'accounts/complete_profile.html', {
        'form': form, 
        'role_title': role_title,
        'departments_exist': departments_exist
    })

@login_required
def dashboard(request):
    user = request.user
    
    # Force profile completion
    if user.role == 'student' and not hasattr(user, 'student_profile'):
        messages.warning(request, "Please complete your student profile first.")
        return redirect('complete_profile')
    elif user.role == 'teacher' and not hasattr(user, 'teacher_profile'):
        messages.warning(request, "Please complete your teacher profile first.")
        return redirect('complete_profile')
        
    # Dynamic Context based on User Role
    context = {
        'user': user,
        'notices': Notice.objects.all().order_by('-created_at')[:5]
    }
    
    if user.role == 'student':
        student = user.student_profile
        context['student'] = student
        
        # Calculate Attendance
        attendances = Attendance.objects.filter(student=student)
        total_days = attendances.count()
        present_days = attendances.filter(status='Present').count()
        context['attendance_pct'] = round((present_days / total_days * 100), 1) if total_days > 0 else 0
        context['total_classes'] = total_days
        context['present_classes'] = present_days
        
        # Upcoming Assignments
        upcoming_assignments = Assignment.objects.filter(
            subject__department=student.department,
            subject__semester=student.semester,
            deadline__gt=timezone.now()
        ).order_by('deadline')
        
        # Add submission status
        for assignment in upcoming_assignments:
            assignment.submitted = Submission.objects.filter(assignment=assignment, student=student).exists()
            
        context['upcoming_assignments'] = upcoming_assignments
        
    elif user.role == 'teacher':
        teacher = user.teacher_profile
        context['teacher'] = teacher
        
        # Teacher's Subjects
        subjects = Subject.objects.filter(teacher=teacher)
        context['subjects'] = subjects
        
        # Assignments Created
        context['total_assignments'] = Assignment.objects.filter(teacher=teacher).count()
        
        # Submissions pending grading
        pending_grading = Submission.objects.filter(
            assignment__teacher=teacher,
            status='Submitted'
        ).count()
        context['pending_grading'] = pending_grading
        
    elif user.is_admin:
        context['total_students'] = Student.objects.count()
        context['total_teachers'] = Teacher.objects.count()
        context['total_departments'] = Department.objects.count()
        context['total_subjects'] = Subject.objects.count()
        
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    user = request.user
    if user.role == 'student':
        profile = getattr(user, 'student_profile', None)
        if not profile:
            return redirect('complete_profile')
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile_view')
        else:
            form = StudentProfileForm(instance=profile)
    elif user.role == 'teacher':
        profile = getattr(user, 'teacher_profile', None)
        if not profile:
            return redirect('complete_profile')
        if request.method == 'POST':
            form = TeacherProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile_view')
        else:
            form = TeacherProfileForm(instance=profile)
    else:
        form = None
        profile = None
        
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def services_view(request):
    return render(request, 'services.html')

def contact_view(request):
    return render(request, 'contact.html')

