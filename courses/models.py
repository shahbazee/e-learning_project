from django.db import models

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    course_type = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    published_status = models.BooleanField(default=False)

def __str__(self):
    return self.name

