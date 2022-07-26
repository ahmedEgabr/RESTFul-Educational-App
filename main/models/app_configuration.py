from django.db import models
from django.core.exceptions import ValidationError
from .time_stamp import TimeStampedModel


class AppConfiguration(TimeStampedModel):

    screenshots_limit = models.IntegerField(blank=True, null=True, verbose_name="Screenshots Limit")
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.is_active and self.__class__.objects.filter(is_active=True).exclude(id=self.id).exists():
            raise ValidationError("Another Active Configurations is already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def is_reached_screenshots_limit(cls, screenshots_num):
        app_config = cls.objects.filter(is_active=True).first()
        if screenshots_num >= app_config.screenshots_limit:
            return True
        return False
