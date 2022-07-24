from django.db import models
from main.models import UserActionModel, TimeStampedModel

class LectureExternalLink(TimeStampedModel):
    lecture = models.ForeignKey("courses.Lecture", on_delete=models.CASCADE, related_name="external_links")
    link = models.URLField(blank=True)
    def __str__(self):
          return self.lecture.title
