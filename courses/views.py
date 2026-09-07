from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from django.shortcuts import render
from .models import Course
from .serializers import CourseSerializer



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

@api_view(['GET', 'POST'])
def course_list_api(request):

    if request.method == 'GET':
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)


        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CourseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status= status.HTTP_404_NOT_FOUND
        )

    