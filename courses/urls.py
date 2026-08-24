from django.urls import path
from . import views

urlpatterns = [
   path('', views.courses_list, name='course_list'),
]

