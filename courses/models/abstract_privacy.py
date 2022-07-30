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
        ('limited_period', 'Public (for a Limited Period)'),
    )

    option = models.CharField(max_length=15, choices=PRIVACY_CHOICES, default=PRIVACY_CHOICES.private)
    shared_with = models.ManyToManyField("users.User", blank=True)

    available_from = models.DateTimeField(
    blank=True,
    null=True,
    help_text="Must be set when choosing public (for a limited period) option."
    )

    period = models.IntegerField(
    blank=True,
    null=True,
    help_text="Must be set when choosing public (for a limited period) option."
    )

    period_type = models.CharField(
    blank=True,
    max_length=10,
    choices=DateFormat.choices,
    help_text="Must be set when choosing public (for a limited period) option."
    )

    enrollment_period = models.IntegerField(
    blank=True,
    null=True,
    verbose_name="When avilable for free, users can enroll it for",
    help_text="""
    The period that the course will be availabe for the user form the date of the enrollment when the course was free.
    Must be set when choosing public (for limited period) option.
    """
    )

    enrollment_period_type = models.CharField(
    blank=True,
    max_length=10,
    choices=DateFormat.choices,
    help_text="Must be set when choosing public (for a limited period) option."
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
        if self.option == self.PRIVACY_CHOICES.limited_period:
            if not self.period:
                raise ValidationError({"period": "Option Public for Limited Period requeires this field to be set."})
            if not self.available_from:
                raise ValidationError({"available_from": "Option Public for Limited Period requeires this field to be set."})
            if not self.period_type:
                raise ValidationError({"period_type": "Option Public for Limited Period requeires this field to be set."})
            if not self.enrollment_period:
                raise ValidationError({"enrollment_period": "Option Public for Limited Period requeires this field to be set."})
            if not self.enrollment_period_type:
                raise ValidationError({"enrollment_period_type": "Option Public for Limited Period requeires this field to be set."})
        super(Privacy, self).clean_fields(**kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Privacy, self).save(*args, **kwargs)


    @property
    def is_public(self):
        return self.option == self.PRIVACY_CHOICES.public

    @property
    def is_public_for_limited_period(self):
        return self.option == self.PRIVACY_CHOICES.limited_period

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
    def is_available_during_limited_period(self):
        if not self.is_public_for_limited_period:
            return False

        current_datetime = timezone.now()
        if current_datetime < self.available_from:
            return False

        period_type = getattr(DateFormat, self.period_type)
        kwargs = {
        f"{period_type}": +self.period
        }
        expiry_date = self.available_from + relativedelta(**kwargs)
        if current_datetime > expiry_date:
            self.reset_privacy_to_private()
            return False
        return True
