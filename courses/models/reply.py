from django.db import models
from main.utility_models import UserActionModel, TimeStampedModel
from courses.managers import ReplyManager


class Reply(UserActionModel, TimeStampedModel):
    discussion = models.ForeignKey("courses.Discussion", on_delete=models.CASCADE, related_name="replies")
    body = models.TextField(blank=True)

    # Custom manager
    objects = ReplyManager()

    def __str__(self):
        return f"{self.id}"
