from django.db import models


class DiscussionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user", "course", "topic", "lecture").prefetch_related("replies")
