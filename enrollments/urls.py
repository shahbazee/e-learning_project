from django.urls import path
from . import views

urlpatterns = [
    path('my-courses/', views.my_courses, name='my_courses'),
]

