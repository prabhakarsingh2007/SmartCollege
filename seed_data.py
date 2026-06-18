import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_college_assistant.settings')
django.setup()

from courses.models import Department, Subject, Timetable
from django.contrib.auth import get_user_model
from teachers.models import Teacher

def seed():
    # 1. Create Departments
    cse, _ = Department.objects.get_or_create(name='Computer Science & Engineering', code='CSE')
    ece, _ = Department.objects.get_or_create(name='Electronics & Communication Engineering', code='ECE')
    me, _ = Department.objects.get_or_create(name='Mechanical Engineering', code='ME')
    
    print("Departments seeded: CSE, ECE, ME")
    
    # 2. Create admin user if not exists
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@college.edu', 'admin123')
        print("Superuser created (username: admin, password: admin123)")
        
    # 3. Create a default Teacher User and Teacher Profile
    if not User.objects.filter(username='prof_sharma').exists():
        teacher_user = User.objects.create_user(
            username='prof_sharma',
            email='sharma@college.edu',
            password='password123',
            first_name='Rakesh',
            last_name='Sharma',
            role='teacher'
        )
        teacher_profile = Teacher.objects.create(
            user=teacher_user,
            employee_id='T101',
            department=cse,
            designation='Assistant Professor',
            phone='9876543210'
        )
        print("Teacher created (username: prof_sharma, password: password123)")
    else:
        teacher_profile = Teacher.objects.get(user__username='prof_sharma')

    # 4. Create Subjects
    sub_dsa, _ = Subject.objects.get_or_create(
        code='CS-301',
        defaults={'name': 'Data Structures & Algorithms', 'department': cse, 'semester': 3, 'teacher': teacher_profile}
    )
    sub_dbms, _ = Subject.objects.get_or_create(
        code='CS-302',
        defaults={'name': 'Database Management Systems', 'department': cse, 'semester': 3, 'teacher': teacher_profile}
    )
    sub_cn, _ = Subject.objects.get_or_create(
        code='CS-303',
        defaults={'name': 'Computer Networks', 'department': cse, 'semester': 3, 'teacher': teacher_profile}
    )
    
    # Update teacher if not set
    sub_dsa.teacher = teacher_profile; sub_dsa.save()
    sub_dbms.teacher = teacher_profile; sub_dbms.save()
    sub_cn.teacher = teacher_profile; sub_cn.save()
    print("Subjects seeded for CSE Sem 3: Data Structures, DBMS, Computer Networks")

    # 5. Create Timetables
    Timetable.objects.get_or_create(
        subject=sub_dsa,
        day='Monday',
        defaults={'start_time': '09:00:00', 'end_time': '10:00:00', 'room_no': 'LH-101'}
    )
    Timetable.objects.get_or_create(
        subject=sub_dbms,
        day='Monday',
        defaults={'start_time': '10:00:00', 'end_time': '11:00:00', 'room_no': 'LH-102'}
    )
    Timetable.objects.get_or_create(
        subject=sub_cn,
        day='Wednesday',
        defaults={'start_time': '11:30:00', 'end_time': '12:30:00', 'room_no': 'LH-101'}
    )
    Timetable.objects.get_or_create(
        subject=sub_dsa,
        day='Friday',
        defaults={'start_time': '14:00:00', 'end_time': '15:00:00', 'room_no': 'LH-101'}
    )
    print("Timetable entries seeded for DSA, DBMS, and CN.")

if __name__ == '__main__':
    seed()
