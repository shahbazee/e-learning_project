from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'description',
            'instructor',
            'price',
            'course_type',
            'created_date',
            'published_status',
        ]