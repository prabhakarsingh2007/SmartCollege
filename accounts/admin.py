from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from students.models import Student
from teachers.models import Teacher

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
