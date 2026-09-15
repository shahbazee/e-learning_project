from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default="Active")
    # Set to True once the payment receipt email has been successfully
    # delivered, so the success page and Stripe webhook can retry safely
    # without spamming the customer.
    receipt_sent = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"