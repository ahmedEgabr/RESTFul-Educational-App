from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from courses.models.abstract_privacy import Privacy
from main.utility_models import DateFormat
from django.core.validators import MinValueValidator, MaxValueValidator
from alteby.utils import render_alert


class CoursePrivacy(Privacy):

    course = models.OneToOneField("courses.Course", on_delete=models.CASCADE, blank=True, related_name="privacy")

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

    is_free = models.BooleanField(
        default=True,
        help_text="Is used when using (for a limited duration) option."
    )
    discount_percentage = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
        blank=True,
        null=True,
        help_text= """
        Is used when using (for a limited duration) option.
        Numbers in %
        """
    )
    show_contact_admin_on_free_enrollment = models.BooleanField(
        default=True,
        verbose_name="Show Contact Admin Button on Free Enrollment",
        help_text= "On uncheck this option, the user can enroll the course automatically when it is free."
    )

    def __str__(self):
          return self.course.title

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
            if not (self.is_free or self.discount_percentage):
                raise ValidationError(
                    render_alert(
                    """
                    You must set is_free or dicsount_percentage.
                    """,
                    alert=True,
                    error=True
                )
            )
        super(CoursePrivacy, self).clean_fields(**kwargs)

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