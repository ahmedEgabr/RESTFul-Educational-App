from django.utils.formats import date_format
from django.utils import timezone
from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import CourseEnrollment


@admin.register(CourseEnrollment, site=main_admin)
class CourseEnrollmentConfig(admin.ModelAdmin):
    model = CourseEnrollment

    list_filter = (
    'user',
    'course',
    'payment_method',
    'payment_type',
    'enrollment_duration',
    'enrollment_duration_type',
    'lifetime_enrollment',
    'enrollment_date',
    )
    ordering = ('-created_at',)
    list_display = ('user', 'course', 'payment_method', 'payment_type', 'enrollment_date', 'is_expired')
    readonly_fields = ("created_at", "enrollment_date", "expiry_date")
    fieldsets = (
        ("Enrollment Information", {'fields':
        (
        'user',
        'course',
        'payment_method',
        'payment_type',
        'enrollment_duration',
        'enrollment_duration_type',
        'lifetime_enrollment',
        'enrollment_date',
        'expiry_date',
        )
        }),
    )

    @staticmethod
    def expiry_date(object):
        if not object.expiry_date:
            return None
        return date_format(timezone.localtime(object.expiry_date), 'DATETIME_FORMAT')
