from django.db import models
from django.contrib.auth.models import User
from courses.models import Course

# Create your models here.
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default='Active')


def __str__(self):
    return f"{self.user.username} - {self.course.name}"