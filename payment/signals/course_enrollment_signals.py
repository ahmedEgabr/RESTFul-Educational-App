from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import CourseEnrollment
from .custom_dispatch import enrollment_duration_changed


@receiver(post_save, sender=CourseEnrollment)
def calculate_expiry_date(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.enrollment_duration and instance.enrollment_duration_type and not instance.expiry_date:
            instance.expiry_date = instance.calculate_expiry_date()
        elif instance.lifetime_enrollment:
            instance.expiry_date = None
        instance.save()

@receiver(enrollment_duration_changed, sender=CourseEnrollment)
def recalculate_expiry_time(sender, instance=None, created=False, **kwargs):
    instance.expiry_date = instance.calculate_expiry_date()
