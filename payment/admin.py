from django.utils.formats import date_format
from django.utils import timezone
from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import CourseEnrollment


@admin.register(CourseEnrollment, site=main_admin)
class CourseEnrollmentConfig(admin.ModelAdmin):
    model = CourseEnrollment
    change_form_template = 'admin/forms/course_enrollment_change_form.html'

    list_filter = (
        'user',
        'course',
        'payment_method',
        'payment_type',
        'enrollment_duration',
        'enrollment_duration_type',
        'lifetime_enrollment',
        'enrollment_date',
        "source_group",
        "promoter"
    )
    ordering = ('-created_at',)
    list_display = ('user', 'course', 'payment_method', 'payment_type', 'enrollment_date', 'is_expired')
    readonly_fields = ("created_at", "created_by", "enrollment_date", "expiry_date")
    fieldsets = (
        ("Enrollment Information", {'fields':
        (
        'user',
        'course',
        'payment_method',
        'payment_type',
        "source_group",
        "promoter",
        'enrollment_duration',
        'enrollment_duration_type',
        'lifetime_enrollment',
        'enrollment_date',
        'expiry_date',
        'force_expiry',
        'is_active',
        'created_by'
        )
        }),
    )
    
    @staticmethod
    def expiry_date(object):
        if not object.calculate_expiry_date:
            return None
        return date_format(timezone.localtime(object.calculate_expiry_date), 'DATETIME_FORMAT')
    
