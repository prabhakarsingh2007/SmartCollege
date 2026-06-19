from google import genai
from google.genai import types
import os

def get_chatbot_response(user, question):
    api_key = os.getenv('GEMINI_API_KEY')
    
    # 1. Gather context depending on user role to make the chatbot context-aware
    context_lines = []
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        profile = user.student_profile
        context_lines.append(f"- Student Name: {user.get_full_name() or user.username}")
        context_lines.append(f"- Department: {profile.department.name} (Code: {profile.department.code})")
        context_lines.append(f"- Current Semester: Semester {profile.semester}")
        context_lines.append(f"- Roll Number: {profile.roll_no}")
        
        # Add Attendance Context
        from attendance.models import Attendance
        attendances = Attendance.objects.filter(student=profile)
        total = attendances.count()
        present = attendances.filter(status='Present').count()
        attendance_pct = round((present / total * 100), 1) if total > 0 else 0
        context_lines.append(f"- Student Attendance Rate: {attendance_pct}% (attended {present} out of {total} classes)")
        
        # Add Timetable Context
        from courses.models import Timetable
        timetable = Timetable.objects.filter(subject__department=profile.department, subject__semester=profile.semester)
        context_lines.append("- Student Class Timetable:")
        for entry in timetable:
            context_lines.append(f"  * {entry.day}: {entry.subject.name} ({entry.subject.code}) from {entry.start_time.strftime('%I:%M %p')} to {entry.end_time.strftime('%I:%M %p')} in Room {entry.room_no}")
            
        # Add Pending Assignments Context
        from assignments.models import Assignment, Submission
        assignments = Assignment.objects.filter(
            subject__department=profile.department,
            subject__semester=profile.semester,
            deadline__gt=timezone_now_stub() # Using helper or query directly
        )
        context_lines.append("- Pending Assignments:")
        for ass in assignments:
            submitted = Submission.objects.filter(assignment=ass, student=profile).exists()
            status = "Submitted" if submitted else "PENDING"
            context_lines.append(f"  * {ass.title} for {ass.subject.name} (Due: {ass.deadline.strftime('%Y-%m-%d %I:%M %p')} - Status: {status})")

    elif user.role == 'teacher' and hasattr(user, 'teacher_profile'):
        profile = user.teacher_profile
        context_lines.append(f"- Teacher Name: {user.get_full_name() or user.username}")
        context_lines.append(f"- Designation: {profile.designation}")
        context_lines.append(f"- Department: {profile.department.name}")
        
        # Add Assigned Subjects
        from courses.models import Subject
        subjects = Subject.objects.filter(teacher=profile)
        context_lines.append("- Assigned Subjects Taught:")
        for sub in subjects:
            context_lines.append(f"  * {sub.name} ({sub.code}) for Semester {sub.semester}")
            
    context_str = "\n".join(context_lines)

    # 2. Call Gemini API or use rich mock fallback if key is missing
    if not api_key:
        return mock_fallback_response(question, context_str)
        
    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = f"""
You are the "Smart College Assistant", an AI helper for students and teachers of our college.
Use the following context about the currently logged-in user to help answer their questions if relevant.
If the context doesn't contain the answer (e.g. general science, coding, math, general questions), answer them using your general knowledge, but maintain your persona.
Always keep answers friendly, helpful, and concise.

User Profile Context:
{context_str}
"""
        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=config
        )
        return response.text
        
    except Exception as e:
        return f"Hello! I am having trouble connecting to my AI core at the moment (Error: {str(e)}). However, based on your profile, here is some information:\n\n{context_str or 'No student details logged yet.'}"

def timezone_now_stub():
    from django.utils import timezone
    return timezone.now()

def mock_fallback_response(question, context_str):
    q_lower = question.lower()
    
    response = "Hello! [DEMO MODE: Gemini API Key not set in .env] "
    
    if "attendance" in q_lower:
        response += "Here is your attendance breakdown:\n\n"
        response += "\n".join([line for line in context_str.split("\n") if "attendance" in line.lower() or "attended" in line.lower()])
    elif "timetable" in q_lower or "class" in q_lower or "schedule" in q_lower:
        response += "Here is your timetable schedule:\n\n"
        timetable_lines = [line for line in context_str.split("\n") if "timetable" in line.lower() or "room" in line.lower() or "*" in line.lower()]
        response += "\n".join(timetable_lines)
    elif "assignment" in q_lower or "homework" in q_lower or "due" in q_lower:
        response += "Here are your assignments:\n\n"
        assignment_lines = [line for line in context_str.split("\n") if "assignment" in line.lower() or "pending" in line.lower() or "due" in line.lower()]
        response += "\n".join(assignment_lines)
    else:
        response += f"You asked: '{question}'. I am ready to answer. Add GEMINI_API_KEY to your .env file to enable full AI responses. Here is your profile summary:\n\n{context_str}"
        
    return response
