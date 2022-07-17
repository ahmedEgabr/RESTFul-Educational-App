from django.db import models
from courses.models import Attachement


class CourseAttachement(Attachement):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="attachments")
    def __str__(self):
          return self.course.title
