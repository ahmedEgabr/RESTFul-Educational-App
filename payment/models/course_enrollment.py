from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib import admin
from model_utils import Choices
from django.conf import settings
from main.utility_models import UserActionModel, TimeStampedModel, DateFormat
from alteby.utils import render_alert


class CourseEnrollment(UserActionModel, TimeStampedModel):

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
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name='enrollments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default=PAYMENT_METHODS.online)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default=PAYMENT_TYPES.free)

    lifetime_enrollment = models.BooleanField(default=False)
    enrollment_duration = models.IntegerField(
        blank=True,
        null=True,
    )

    enrollment_duration_type = models.CharField(
        blank=True,
        null=True,
        max_length=10,
        choices=DateFormat.choices,
    )

    enrollment_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    force_expiry = models.BooleanField(
        default=False, 
        help_text=render_alert(
            """
            &#x26A0; When checked, 
            This enrollment will be expired before its expiry date even if it is lifetime enrollment.
            """,
            tag="strong",
            warning=True
        )
    )
    source_group = models.ForeignKey(
        "users.SourceGroup", 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE
    )
    promoter = models.ForeignKey(
        "users.User",
        null=True, 
        blank=True,
        on_delete=models.CASCADE, 
        related_name="enrollments_contributions",
        limit_choices_to={"is_promoter": True},
    )
    is_active = models.BooleanField(default=True, help_text=render_alert(
        message="&#x26A0; When not ckecked, this enrollment will be deactivated.",
        tag="strong",
        warning=True
        )
    )

    def clean_fields(self, **kwargs):
        if self.force_expiry:
            return None
        
        if not self.enrollment_duration and self.enrollment_duration_type and not self.lifetime_enrollment:
            raise ValidationError({"enrollment_duration": "This field is required"})

        if not self.enrollment_duration_type and self.enrollment_duration and not self.lifetime_enrollment:
            raise ValidationError({"enrollment_duration_type": "This field is required."})

        super(CourseEnrollment, self).clean_fields(**kwargs)

    def calculate_expiry_date(self):
        if not (self.enrollment_duration and self.enrollment_duration_type):
            return None
        enrollment_duration_type = getattr(DateFormat, self.enrollment_duration_type)
        kwargs = {
        f"{enrollment_duration_type}": +self.enrollment_duration
        }
        return self.enrollment_date + relativedelta(**kwargs)

    @admin.display(boolean=True)
    def is_expired(self):
        if self.lifetime_enrollment:
            return False

        if self.enrollment_duration and self.enrollment_duration_type:
            current_datetime = timezone.now()

            if current_datetime < self.expiry_date:
                return False
        return True

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.lifetime_enrollment:
            self.enrollment_duration = None
            self.enrollment_duration_type = None
        if self.id:
            old_instance = self.__class__.objects.get(id=self.id)
            if (old_instance.enrollment_duration != self.enrollment_duration) or (
                old_instance.enrollment_duration_type != self.enrollment_duration_type
            ): 
                from payment.signals.custom_dispatch import enrollment_duration_changed
                enrollment_duration_changed.send(sender=type(self), instance=self)
        return super(CourseEnrollment, self).save(*args, **kwargs)
