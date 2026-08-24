from django.shortcuts import render

# Create your views here.

def courses_list(request):
    return render(request, "courses/courses_list.html")
