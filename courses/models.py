from django.db import models

# Static course-image map: course name keywords -> static image path (relative to STATIC_URL).
# Used whenever a course does not have an explicit image set.
COURSE_IMAGE_BY_NAME = {
    "python": "img/courses/python.svg",
    "javascript": "img/courses/javascript.svg",
    "django": "img/courses/django.svg",
    "sql": "img/courses/database.svg",
    "database": "img/courses/database.svg",
    "mysql": "img/courses/database.svg",
    "postgres": "img/courses/database.svg",
    "c#": "img/courses/csharp.svg",
    "csharp": "img/courses/csharp.svg",
    "dotnet": "img/courses/csharp.svg",
    "git": "img/courses/git.svg",
    "github": "img/courses/git.svg",
}
DEFAULT_COURSE_IMAGE = "img/courses/default.svg"


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    course_type = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    published_status = models.BooleanField(default=False)
    # Optional course image uploaded in the admin (stored under MEDIA_ROOT/media/courses/).
    # When no image is uploaded, a professional image is derived from the course
    # name via ``image_url()`` instead of breaking the card.
    image = models.ImageField(upload_to="courses/", blank=True, null=True)

    def image_url(self):
        """Static fallback path used via ``{% static course.image_url %}``
        when the course has no uploaded image."""
        lowered = (self.name or "").strip().lower()
        for keyword, path in COURSE_IMAGE_BY_NAME.items():
            if keyword in lowered:
                return path
        return DEFAULT_COURSE_IMAGE

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    """Contact-form submissions, stored so admins can follow up."""
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Contact messages"

    def __str__(self):
        return f"{self.subject} — {self.email}"
