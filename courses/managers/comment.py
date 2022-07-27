from django.db import models


class CommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user", "object_type").prefetch_related("replies")
