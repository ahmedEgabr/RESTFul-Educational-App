from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from model_utils import Choices
from main.utility_models import UserActionModel, TimeStampedModel, DateFormat


class Privacy(UserActionModel, TimeStampedModel):

    class AvailabilityStatus(models.IntegerChoices):
        DISABLED = 0, "Disabled" 
        AVAILABLE_FOR_ALL_USERS = 1, "Available for all users"
        AVAILABLE_FOR_ENROLLED = 2, "Available ONLY for Enrolled Users"
    
    class PrivacyType(models.TextChoices):
        PUBLIC = "public", "Public" 
        PRIVATE = "private", "Private"
        SHARED = "shared", "Shared"
        LIMITED_DURATION = "limited_duration", "Public (for a Limited duration)"

    option = models.CharField(max_length=20, choices=PrivacyType.choices, default=PrivacyType.PRIVATE)
    shared_with = models.ManyToManyField("users.User", blank=True)
    attachments_status = models.IntegerField(choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE_FOR_ENROLLED)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Privacy, self).save(*args, **kwargs)


    @property
    def is_public(self):
        return self.option == self.PrivacyType.PUBLIC

    @property
    def is_public_for_limited_duration(self):
        return self.option == self.PrivacyType.LIMITED_DURATION

    @property
    def is_private(self):
        return self.option == self.PrivacyType.PRIVATE

    @property
    def is_shared(self):
        return self.option == self.PrivacyType.SHARED

    def reset_privacy_to_private(self):
        self.option = self.PrivacyType.PRIVATE
        self.save()

    @property
    def is_available_during_limited_duration(self):
        if not self.is_public_for_limited_duration:
            return False

        current_datetime = timezone.now()
        if current_datetime < self.available_from:
            return False

        duration_type = getattr(DateFormat, self.duration_type)
        kwargs = {
        f"{duration_type}": +self.duration
        }
        expiry_date = self.available_from + relativedelta(**kwargs)
        if current_datetime > expiry_date:
            self.reset_privacy_to_private()
            return False
        return True
