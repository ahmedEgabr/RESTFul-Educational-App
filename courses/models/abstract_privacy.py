from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from model_utils import Choices
from main.utility_models import UserActionModel, TimeStampedModel, DateFormat


class Privacy(UserActionModel, TimeStampedModel):

    PRIVACY_CHOICES = Choices(
        ('public', 'Public'),
        ('private', 'Private'),
        ('shared', 'Shared'),
        ('limited_duration', 'Public (for a Limited duration)'),
    )

    option = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default=PRIVACY_CHOICES.private)
    shared_with = models.ManyToManyField("users.User", blank=True)

    available_from = models.DateTimeField(
    blank=True,
    null=True,
    help_text="Must be set when choosing public (for a limited duration) option."
    )

    duration = models.IntegerField(
    blank=True,
    null=True,
    help_text="Must be set when choosing public (for a limited duration) option."
    )

    duration_type = models.CharField(
    blank=True,
    max_length=10,
    choices=DateFormat.choices,
    help_text="Must be set when choosing public (for a limited duration) option."
    )

    enrollment_duration = models.IntegerField(
    blank=True,
    null=True,
    verbose_name="When avilable for free, users can enroll it for",
    help_text="""
    The duration that the course will be availabe for the user form the date of the enrollment when the course was free.
    Must be set when choosing public (for limited duration) option.
    """
    )

    enrollment_duration_type = models.CharField(
    blank=True,
    max_length=10,
    choices=DateFormat.choices,
    help_text="Must be set when choosing public (for a limited duration) option."
    )

    is_downloadable = models.BooleanField(default=True, verbose_name="Is Downloadable")
    is_downloadable_for_enrolled_users_only = models.BooleanField(
    default=True,
    verbose_name="Is Downloadable for Enrolled Users Only"
    )

    is_quiz_available = models.BooleanField(default=True, verbose_name="Is Quiz Available")
    is_quiz_available_for_enrolled_users_only = models.BooleanField(
    default=True,
    verbose_name="Is Quiz Available for Enrolled Users Only"
    )

    is_attachements_available = models.BooleanField(default=True, verbose_name="Is Attachemets Available")
    is_attachements_available_for_enrolled_users_only = models.BooleanField(
    default=True,
    verbose_name="Is Attachements Available for Enrolled Users Only",
    )

    class Meta:
        abstract = True

    def clean_fields(self, **kwargs):
        if self.option == self.PRIVACY_CHOICES.limited_duration:
            if not self.duration:
                raise ValidationError({"duration": "Option Public for Limited Duration requeires this field to be set."})
            if not self.available_from:
                raise ValidationError({"available_from": "Option Public for Limited Duration requeires this field to be set."})
            if not self.duration:
                raise ValidationError({"duration_type": "Option Public for Limited Duration requeires this field to be set."})
            if not self.enrollment_duration:
                raise ValidationError({"enrollment_duration": "Option Public for Limited Duration requeires this field to be set."})
            if not self.enrollment_duration_type:
                raise ValidationError({"enrollment_duration_type": "Option Public for Limited Duration requeires this field to be set."})
        super(Privacy, self).clean_fields(**kwargs)

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
