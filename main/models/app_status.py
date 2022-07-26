import os
from django.db import models
from django.core.exceptions import ValidationError
from .time_stamp import TimeStampedModel


class AppStatus(TimeStampedModel):
    """ AppStatus model """

    is_online = models.BooleanField(default=True)
    is_under_maintenance = models.BooleanField(default=True)
    reason = models.TextField(blank=True)
    downtime_till = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "App Status"
        verbose_name_plural = "App Status"

    def save(self, *args, **kwargs):
        if not self.pk and AppStatus.objects.exists():
        # if you'll not check for self.pk
        # then error will also raised in update of exists model
            raise ValidationError('There is can be only one AppStatus.')
        return super(AppStatus, self).save(*args, **kwargs)
