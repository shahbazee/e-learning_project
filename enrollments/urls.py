from django.urls import path
from . import views

urlpatterns = [
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path("my-enrollments/", views.my_enrollments, name="my_enrollments"),
    path("enrollment/<int:enrollment_id>/", views.enrollment_detail, name="enrollment_detail"),
]

