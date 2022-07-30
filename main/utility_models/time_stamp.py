from django.db import models


class TimeStampedModel(models.Model):
    """
    Provides created_at updated_at fields
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        abstract = True
