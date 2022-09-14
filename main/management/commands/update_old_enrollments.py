# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Local Django
from payment.models import CourseEnrollment
from main.utility_models import DateFormat


class Command(BaseCommand):
    help = 'Update old enrollments'

    def handle(self, *args, **kwargs):
        enrollments = CourseEnrollment.objects.all()
        for enrollment in enrollments:
            enrollment.enrollment_duration = 2
            enrollment.enrollment_duration_type = DateFormat.years
            enrollment.save()
        self.stdout.write(self.style.SUCCESS("Done."))
        