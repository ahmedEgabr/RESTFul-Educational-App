from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import Category, ReferenceCategory, Tag


class ReferenceCategoryConfig(admin.ModelAdmin):
    model = ReferenceCategory

    list_filter = ('created_by', 'created_at')
    ordering = ('-created_at',)
    list_display = ('name', )
    readonly_fields = ('created_by', 'updated_by', 'created_at')

main_admin.register(Category)
main_admin.register(ReferenceCategory, ReferenceCategoryConfig)
main_admin.register(Tag)
