from django.db import models


class ReplyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("created_by", "updated_by")
