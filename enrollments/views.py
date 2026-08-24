from django.shortcuts import render

# Create your views here.

def my_courses(request):
    return render(request, "enrollments/my_courses.html")

