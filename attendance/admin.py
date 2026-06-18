from django.contrib import admin
from .models import Attendance, QRSession

admin.site.register(Attendance)
admin.site.register(QRSession)
