from django.db import models
from main.models import UserActionModel, TimeStampedModel
from courses.managers import ReplyManager


class Reply(UserActionModel, TimeStampedModel):
    comment = models.ForeignKey("courses.Comment", on_delete=models.CASCADE, related_name="replies")
    body = models.CharField(blank=True, max_length=100)

    # Custom manager
    objects = ReplyManager()

    def __str__(self):
        return f"{self.id}"
