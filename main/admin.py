from django.contrib import admin
from django import forms
from django.utils.formats import date_format
from django.utils import timezone
from alteby.admin_sites import main_admin, promoter_admin
from .models import ContactUs, AppVersion, AppStatus, AppConfiguration
from payment.models import CourseEnrollment


@admin.register(AppConfiguration, site=main_admin)
class AppConfigurationConfig(admin.ModelAdmin):
    list_filter = ('is_active', 'screenshots_limit')
    ordering = ('-created_at',)
    list_display = ('screenshots_limit', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
        'fields': (
        'screenshots_limit',
        'is_active'
        )}),
    )


@admin.register(AppVersion, site=main_admin)
class AppVersionConfig(admin.ModelAdmin):
    list_filter = ('version_code', 'version_name', 'is_active', 'is_minimum_version', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_display = ('version_name', 'is_active', 'is_minimum_version')
    readonly_fields = ('created_at', 'updated_at', 'version_code')

    fieldsets = (
        (None, {
        'fields': (
        'version_name',
        'version_code',
        'description',
        'is_minimum_version',
        'is_active'
        )}),
    )


@admin.register(AppStatus, site=main_admin)
class AppStatusConfig(admin.ModelAdmin):
    list_display = ('is_online', 'is_under_maintenance', 'downtime_till')
    readonly_fields = ('created_at', 'updated_at')
    change_form_template = 'main/forms/app_status_change_form.html'
    fieldsets = (
        (None, {
        'fields': (
        'is_online',
        'is_under_maintenance',
        'reason',
        'downtime_till',
        )}),
    )

    def has_add_permission(self, request):
        # check if generally has add permission
        is_allowed = super().has_add_permission(request)
        # set add permission to False, if object already exists
        if is_allowed and self.model.objects.exists():
            is_allowed = False
        return is_allowed


@admin.register(ContactUs, site=main_admin)
class ContactUsConfig(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'telegram_username', 'messenger_username')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
        'fields': (
        'email',
        'phone_number',
        'telegram_username',
        'messenger_username',
        )}),
    )

    def has_add_permission(self, request):
        # check if generally has add permission
        is_allowed = super().has_add_permission(request)
        # set add permission to False, if object already exists
        if is_allowed and self.model.objects.exists():
            is_allowed = False
        return is_allowed
    
@admin.register(CourseEnrollment, site=promoter_admin)
class CourseEnrollmentPromoterAdmin(admin.ModelAdmin):
    
    class CourseEnrollmentForm(forms.ModelForm):
        class Meta:
            model = CourseEnrollment
            fields = '__all__'
            help_texts = {"is_active": None, "force_expiry": None}
            
    change_form_template = 'admin/forms/course_enrollment_change_form.html'
    form = CourseEnrollmentForm
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


    def get_queryset(self, request):
        queryset = super(CourseEnrollmentPromoterAdmin, self).get_queryset(request)
        return queryset.select_related("course").filter(promoter=request.user)
    
    @staticmethod
    def expiry_date(object):
        if not object.calculate_expiry_date:
            return None
        return date_format(timezone.localtime(object.calculate_expiry_date), 'DATETIME_FORMAT')