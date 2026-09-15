from django.contrib import admin
from .models import ContactMessage, Course


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
    list_filter = ('published_status', 'course_type')
    search_fields = ('name', 'instructor', 'description')
    list_editable = ('published_status',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')