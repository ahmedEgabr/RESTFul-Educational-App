from django.db import models
from django.core.exceptions import ValidationError
from main.utility_models import TimeStampedModel, UserActionModel, DateFormat
from alteby.utils import render_alert


class CoursePricingPlan(TimeStampedModel, UserActionModel):

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="pricing_plans")

    duration = models.IntegerField(
    blank=True,
    null=True,
    )

    duration_type = models.CharField(
    blank=True,
    null=True,
    max_length=10,
    choices=DateFormat.choices,
    )

    lifetime_access = models.BooleanField(default=False)
    is_free_for_all_countries = models.BooleanField(default=False, help_text=render_alert(
        message="&#9888; When checked, all plan prices is going to be deactivated.",
        tag="small",
        warning=True
        ))
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text=render_alert(
        message="&#x26A0; When not ckecked, this price will not be visable to the students.",
        tag="small",
        warning=True
        ))
                                    
    class Meta:
        verbose_name_plural = 'Courses Pricing Plans'
        unique_together = (
        ("course", "duration", "duration_type"),
        )

    def __str__(self):
        return f"course-{self.course.title}"

    def clean_fields(self, **kwargs):
        if not self.is_active:
            return None
        
        if not self.duration and self.duration_type:
            raise ValidationError({"duration": "This field is required."})

        if not self.duration_type and self.duration:
            raise ValidationError({"duration_type": "This field is required."})

        if not (self.duration or self.duration_type or self.lifetime_access):
            raise ValidationError(
            "You have to specify the course price plan (Lifetime Access or Duration)."
            )

        # if self.duration and self.duration_type and self.lifetime_access:
        #     raise ValidationError(
        #         "Plan must be whether Lifetime Access or limited with Duration and Duration Type, not Both."
        #     )

        if not self.is_active:
            return None

        if self.lifetime_access:
            exists = self.__class__.objects.filter(
            course=self.course, lifetime_access=True, is_active=True
            ).exclude(id=self.id)

            if exists:
                raise ValidationError(
                    "Course Price with LifeTime Access is already exists."
                )

        if self.is_default:

            exists = self.__class__.objects.filter(
            course=self.course, is_default=True, is_active=True
            ).exclude(id=self.id)

            if exists:
                raise ValidationError(
                    {
                        "is_default": render_alert(
                            message="Course Price with Default is already exists.",
                            tag="small",
                            error=True
                            )
                    }
                )
        super(CoursePricingPlan, self).clean_fields(**kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(CoursePricingPlan, self).save(*args, **kwargs)

    @classmethod
    def create_default_pricing_plan(cls, course):

        if course.has_pricing_plans:
            return None

        return cls.objects.create(
        course=course,
        lifetime_access=True,
        is_default=True
        )
    
    def has_default_price(self, excluded_ids=[]):
        return self.prices.filter(is_active=True, is_default=True).exclude(id__in=excluded_ids).exists()
