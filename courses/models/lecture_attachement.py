from django.db import models
from courses.models import Attachement

class LectureAttachement(Attachement):
    lecture = models.ForeignKey("courses.Lecture", on_delete=models.CASCADE, related_name="attachments")
    def __str__(self):
          return self.lecture.title
