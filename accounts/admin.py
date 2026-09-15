from django.contrib import admin
from .models import EmailOTP


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "created_at", "expires_at")
    list_filter = ("purpose", "expires_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at",)
