from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.

from .models import Enrollment
from courses.models import Course


def my_courses(request):
    return render(request, "enrollments/my_courses.html")


    return redirect("my_enrollments")

@login_required
def my_enrollments(request):
    enrollments = Enrollment.objects.filter(user= request.user)

    return render(request, "enrollments/my_enrollments.html", {"enrollments": enrollments})


@login_required
def enrollment_detail(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        user = request.user
    )

    return render(request, "enrollments/enrollment_detail.html", {"enrollment": enrollment})

@login_required
def enroll_course(request, course_id):

    # Find the course selected by the user
    course = get_object_or_404(Course, id=course_id)

    Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )
    return redirect('my_enrollments')