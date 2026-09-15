from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "progress", "enrollment_date")
    list_filter = ("status", "enrollment_date")
    search_fields = ("user__username", "user__email", "course__name")