from django.contrib import admin
from .models import Course
# Register your models here.



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'instructor',
        'price',
        'course_type',
        'created_date',
        'published_status',
    )