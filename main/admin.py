from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import ContactUs, AppVersion, AppStatus

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
        if is_allowed and AppStatus.objects.exists():
            is_allowed = False
        return is_allowed

main_admin.register(ContactUs)
