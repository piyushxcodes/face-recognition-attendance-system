from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_student, name='register_student'),
    path('train/', views.train_model, name='train_model'),
    path('attendance/', views.take_attendance, name='take_attendance'),
    path('reports/', views.attendance_report, name='attendance_report'),
]