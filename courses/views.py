from django.shortcuts import render
from .models import Course

def home(request):
    return render(request, "courses/home.html", {"courses": Course.objects.all()})


def courses_list(request):
    courses = Course.objects.all()
    return render(request, "courses/courses_list.html", {
        "courses": courses
    })


def courses_detail(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return render(request, "404.html")

    return render(request, "courses/courses_detail.html", {"course": course})


def search_courses(request):
    search = request.GET.get("search")
    if search:
        courses = Course.objects.filter(name__icontains= search)
    else:
        course = Course.objects.all()

    return render(request, "courses/courses_list.html", {"courses": courses})



def filter_courses(request):
    course_type = request.GET.get("course_type")

    if course_type:
        courses = Course.objects.filter(course_type = course_type)
    else:
        course = Course.objects.all()

    return render(request, "courses/courses_list.html", {
        "courses": courses
    })


def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

