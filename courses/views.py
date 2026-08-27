from django.shortcuts import render


def home(request):
    return render(request, "courses/home.html")


def courses_list(request):
    return render(request, "courses/courses_list.html")