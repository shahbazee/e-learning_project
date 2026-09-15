from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

OTP_EXPIRY_MINUTES = 15


def _default_otp_expiry():
    return timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)


class EmailOTP(models.Model):
    PURPOSE_SIGNUP = "signup"
    PURPOSE_RESET = "reset"

    PURPOSE_CHOICES = [
        (PURPOSE_SIGNUP, "Signup"),
        (PURPOSE_RESET, "Password Reset"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    otp = models.CharField(max_length=6)

    purpose = models.CharField(
        max_length=10,
        choices=PURPOSE_CHOICES,
        default=PURPOSE_SIGNUP,
    )

    created_at = models.DateTimeField(auto_now=True)

    expires_at = models.DateTimeField(default=_default_otp_expiry)

    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.otp} ({self.purpose})"