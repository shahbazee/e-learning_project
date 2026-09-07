from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.courses_list, name='course_list'),
    path('courses/<int:course_id>/', views.courses_detail, name='courses_detail'),
    path('search/', views.search_courses, name='search_courses'),
    path('filter/', views.filter_courses, name='filter_courses'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('api/courses/', views.course_list_api, name='course_list_api'),
]

