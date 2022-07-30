from django.db import models
from main.utility_models import TimeStampedModel


class Note(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="lectures_notes")
    lecture = models.ForeignKey("courses.Lecture", on_delete=models.CASCADE, related_name="notes")
    note = models.TextField()

    def __str__(self):
        return f"{self.user.id}-note on-{self.lecture.id}"
