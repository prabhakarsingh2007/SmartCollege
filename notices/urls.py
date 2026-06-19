from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_notice, name='create_notice'),
    path('latest/', views.latest_notice_api, name='latest_notice_api'),
]
