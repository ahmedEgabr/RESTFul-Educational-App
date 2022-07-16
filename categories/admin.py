from django.contrib import admin
from .models import Category, ReferenceCategory, Tag

class ReferenceCategoryConfig(admin.ModelAdmin):
    model = ReferenceCategory

    list_filter = ('created_by', 'created_at')
    ordering = ('-created_at',)
    list_display = ('name', )
    readonly_fields = ('created_by', 'updated_by', 'created_at')

admin.site.register(Category)
admin.site.register(ReferenceCategory, ReferenceCategoryConfig)
admin.site.register(Tag)
