from django.db import models
from . import Price


class CoursePrice(Price):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="prices")

    class Meta:
        unique_together = ["course", "currency"]
