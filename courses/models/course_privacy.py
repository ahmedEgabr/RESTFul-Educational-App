from django.db import models
from courses.models.abstract_privacy import Privacy


class CoursePrivacy(Privacy):

    course = models.OneToOneField("courses.Course", on_delete=models.CASCADE, blank=True, related_name="privacy")

    def __str__(self):
          return self.course.title
