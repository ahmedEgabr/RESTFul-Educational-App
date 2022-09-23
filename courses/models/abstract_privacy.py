from django.db import models
from django.core.exceptions import ValidationError
from model_utils import Choices
from main.utility_models import UserActionModel, TimeStampedModel


class Privacy(UserActionModel, TimeStampedModel):

    PRIVACY_CHOICES = Choices(
        ('public', 'Public'),
        ('private', 'Private'),
        ('shared', 'Shared'),
        ('limited_duration', 'Public (for a Limited duration)'),
    )

    option = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default=PRIVACY_CHOICES.private)
    shared_with = models.ManyToManyField("users.User", blank=True)

    is_attachements_available = models.BooleanField(default=True, verbose_name="Is Attachemets Available")
    is_attachements_available_for_enrolled_users_only = models.BooleanField(
    default=True,
    verbose_name="Is Attachements Available for Enrolled Users Only",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Privacy, self).save(*args, **kwargs)


    @property
    def is_public(self):
        return self.option == self.PRIVACY_CHOICES.public

    @property
    def is_public_for_limited_duration(self):
        return self.option == self.PRIVACY_CHOICES.limited_duration

    @property
    def is_private(self):
        return self.option == self.PRIVACY_CHOICES.private

    @property
    def is_shared(self):
        return self.option == self.PRIVACY_CHOICES.shared

    def reset_privacy_to_private(self):
        self.option = self.PRIVACY_CHOICES.private
        self.save()

    
