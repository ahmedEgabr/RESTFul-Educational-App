from django.db import models
from courses.models.abstract_privacy import Privacy

class LecturePrivacy(Privacy):

    lecture = models.OneToOneField("courses.Lecture", on_delete=models.CASCADE, blank=True, related_name="privacy")

    def __str__(self):
          return self.lecture.title
