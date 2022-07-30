from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib import admin
from courses.models import Course
from model_utils import Choices
from django.conf import settings
from main.utility_models import UserActionModel, TimeStampedModel
UserModel = settings.AUTH_USER_MODEL


class CourseEnrollment(UserActionModel, TimeStampedModel):

    class DateFormat(models.TextChoices):
        days = "days", ("Days")
        weeks = "weeks", ("Weeks")
        months = "months", ("Months")
        years = "years", ("Years")

    PAYMENT_METHODS = Choices(
        ('online', 'Online'),
        ('offline', 'Offline'),
    )

    PAYMENT_TYPES = Choices(
        ('telegram', 'Telegram'),
        ('fawry', 'Fawry'),
        ('visa', 'Visa'),
        ('free', 'Free'),
    )
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default=PAYMENT_METHODS.online)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default=PAYMENT_TYPES.free)

    is_enrolled_for_life_long = models.BooleanField(default=False)
    enrollment_duration = models.IntegerField(
    blank=True,
    null=True,
    )

    enrollment_duration_type = models.CharField(
    blank=True,
    max_length=10,
    choices=DateFormat.choices,
    )

    enrollment_date = models.DateTimeField(auto_now_add=True)

    def clean_fields(self, **kwargs):
        if not self.enrollment_duration and self.enrollment_duration_type:
            raise ValidationError({"enrollment_duration": "This field is required"})

        if not self.enrollment_duration_type and self.enrollment_duration:
            raise ValidationError({"enrollment_duration_type": "This field is required."})

        super(CourseEnrollment, self).clean_fields(**kwargs)

    @property
    def expiry_date(self):
        if not (self.enrollment_duration and self.enrollment_duration_type):
            return None
        enrollment_duration_type = getattr(self.DateFormat, self.enrollment_duration_type)
        kwargs = {
        f"{enrollment_duration_type}": +self.enrollment_duration
        }
        return self.enrollment_date + relativedelta(**kwargs)

    @admin.display(boolean=True)
    def is_expired(self):
        if self.is_enrolled_for_life_long:
            return False

        if self.enrollment_duration and self.enrollment_duration_type:
            current_datetime = timezone.now()

            if current_datetime < self.expiry_date:
                return False
        return True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(CourseEnrollment, self).save(*args, **kwargs)
