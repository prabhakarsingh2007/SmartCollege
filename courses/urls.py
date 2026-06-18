from django.urls import path
from . import views

urlpatterns = [
    path('timetable/', views.timetable_view, name='timetable_view'),
]
