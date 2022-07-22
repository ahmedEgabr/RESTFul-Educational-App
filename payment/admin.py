from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import CourseEnrollment

class CourseEnrollmentConfig(admin.ModelAdmin):
    model = CourseEnrollment

    list_filter = ('user', 'course', 'payment_method', 'payment_type', 'date_created')
    ordering = ('-date_created',)
    list_display = ('user', 'course', 'payment_method', 'payment_type', 'date_created')

    fieldsets = (
        ("Course Enrollment Information", {'fields': ('user', 'course', 'payment_method', 'payment_type')}),
    )

main_admin.register(CourseEnrollment, CourseEnrollmentConfig)
