from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
        return redirect('home')
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
        
        # Attendance by Subject
        student_subjects = Subject.objects.filter(department=student.department, semester=student.semester)
        subject_names = []
        subject_pcts = []
        for subj in student_subjects:
            s_total = Attendance.objects.filter(student=student, subject=subj).count()
            s_present = Attendance.objects.filter(student=student, subject=subj, status='Present').count()
            s_pct = round((s_present / s_total * 100), 1) if s_total > 0 else 0
            subject_names.append(subj.name)
            subject_pcts.append(s_pct)
        context['subject_names'] = subject_names
        context['subject_pcts'] = subject_pcts
        
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
        
        # Attendance averages for teacher's subjects
        teacher_subject_names = []
        teacher_attendance_averages = []
        for subj in subjects:
            s_attendances = Attendance.objects.filter(subject=subj)
            total = s_attendances.count()
            present = s_attendances.filter(status='Present').count()
            avg = round((present / total * 100), 1) if total > 0 else 0
            teacher_subject_names.append(subj.name)
            teacher_attendance_averages.append(avg)
        context['teacher_subject_names'] = teacher_subject_names
        context['teacher_attendance_averages'] = teacher_attendance_averages
        
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

@login_required
def custom_admin_panel(request):
    user = request.user
    if not user.is_admin:
        messages.error(request, "Access denied. Only administrators can access the admin panel.")
        return redirect('dashboard')
        
    active_tab = request.GET.get('tab', 'overview')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_department':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            if name and code:
                if Department.objects.filter(code=code).exists():
                    messages.error(request, f"Department code '{code}' already exists.")
                else:
                    Department.objects.create(name=name, code=code)
                    messages.success(request, f"Department '{name}' created successfully!")
            else:
                messages.error(request, "All fields are required.")
                
        elif action == 'edit_department':
            dept_id = request.POST.get('id')
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            dept = get_object_or_404(Department, id=dept_id)
            if name and code:
                if Department.objects.filter(code=code).exclude(id=dept_id).exists():
                    messages.error(request, f"Department code '{code}' already exists.")
                else:
                    dept.name = name
                    dept.code = code
                    dept.save()
                    messages.success(request, "Department updated successfully!")
            else:
                messages.error(request, "All fields are required.")
                
        elif action == 'delete_department':
            dept_id = request.POST.get('id')
            dept = get_object_or_404(Department, id=dept_id)
            try:
                dept.delete()
                messages.success(request, "Department deleted successfully.")
            except Exception as e:
                messages.error(request, "Could not delete department. It may have associated students or teachers.")
                
        elif action == 'add_subject':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            dept_id = request.POST.get('department')
            semester = request.POST.get('semester')
            teacher_id = request.POST.get('teacher')
            
            if name and code and dept_id and semester:
                dept = get_object_or_404(Department, id=dept_id)
                teacher = None
                if teacher_id:
                    teacher = get_object_or_404(Teacher, id=teacher_id)
                if Subject.objects.filter(code=code).exists():
                    messages.error(request, f"Subject code '{code}' already exists.")
                else:
                    Subject.objects.create(
                        name=name, code=code, department=dept, 
                        semester=int(semester), teacher=teacher
                    )
                    messages.success(request, f"Subject '{name}' created successfully!")
            else:
                messages.error(request, "All required fields must be filled.")
                
        elif action == 'edit_subject':
            sub_id = request.POST.get('id')
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            dept_id = request.POST.get('department')
            semester = request.POST.get('semester')
            teacher_id = request.POST.get('teacher')
            
            sub = get_object_or_404(Subject, id=sub_id)
            if name and code and dept_id and semester:
                dept = get_object_or_404(Department, id=dept_id)
                teacher = None
                if teacher_id:
                    teacher = get_object_or_404(Teacher, id=teacher_id)
                if Subject.objects.filter(code=code).exclude(id=sub_id).exists():
                    messages.error(request, f"Subject code '{code}' already exists.")
                else:
                    sub.name = name
                    sub.code = code
                    sub.department = dept
                    sub.semester = int(semester)
                    sub.teacher = teacher
                    sub.save()
                    messages.success(request, "Subject updated successfully!")
            else:
                messages.error(request, "All required fields must be filled.")
                
        elif action == 'delete_subject':
            sub_id = request.POST.get('id')
            sub = get_object_or_404(Subject, id=sub_id)
            sub.delete()
            messages.success(request, "Subject deleted successfully.")
            
        elif action == 'add_timetable':
            sub_id = request.POST.get('subject')
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            room_no = request.POST.get('room_no', '').strip()
            
            if sub_id and day and start_time and end_time and room_no:
                subject = get_object_or_404(Subject, id=sub_id)
                Timetable.objects.create(
                    subject=subject, day=day, start_time=start_time, 
                    end_time=end_time, room_no=room_no
                )
                messages.success(request, "Timetable entry added successfully!")
            else:
                messages.error(request, "All fields are required.")
                
        elif action == 'delete_timetable':
            entry_id = request.POST.get('id')
            entry = get_object_or_404(Timetable, id=entry_id)
            entry.delete()
            messages.success(request, "Timetable slot deleted successfully.")
            
        return redirect(f"{reverse('custom_admin_panel')}?tab={active_tab}")
        
    # GET Request: Prepare Context based on tab
    context = {
        'active_tab': active_tab,
    }
    
    if active_tab == 'overview':
        context['total_students'] = Student.objects.count()
        context['total_teachers'] = Teacher.objects.count()
        context['total_departments'] = Department.objects.count()
        context['total_subjects'] = Subject.objects.count()
        context['notices'] = Notice.objects.all().order_by('-created_at')[:5]
        
    elif active_tab == 'departments':
        context['departments'] = Department.objects.all().order_by('code')
        
    elif active_tab == 'subjects':
        context['subjects'] = Subject.objects.all().order_by('department__code', 'semester', 'code')
        context['departments'] = Department.objects.all().order_by('code')
        context['teachers'] = Teacher.objects.all().order_by('user__first_name', 'user__username')
        
    elif active_tab == 'timetable':
        context['timetable'] = Timetable.objects.all().order_by('day', 'start_time')
        context['subjects'] = Subject.objects.all().order_by('code')
        
    elif active_tab == 'users':
        context['students'] = Student.objects.all().order_by('department__code', 'semester', 'roll_no')
        context['teachers'] = Teacher.objects.all().order_by('department__code', 'user__username')
        
    return render(request, 'accounts/admin_panel.html', context)

