from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import Question, Choice, QuestionAnswer


class ChoiceInline(admin.StackedInline):
    model = Choice
    can_delete = True
    max_num = 4
    extra = 1
    verbose_name_plural = 'Choices'
    fk_name = 'question'


@admin.register(Question, site=main_admin)
class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_filter = ('title', 'is_active', 'created_at', 'created_by')
    list_display = ('reference', 'title', 'is_active', 'created_at', 'created_by')
    readonly_fields = ('created_by', 'created_at')
    fieldsets = (
        (None, {'fields': ('title', 'extra_info', 'image', 'is_active')}),
    )
    
    inlines = [ChoiceInline]
    
@admin.register(QuestionAnswer, site=main_admin)
class QuestionAnswerAdmin(admin.ModelAdmin):
    model = QuestionAnswer
    list_filter = ('user', 'question', 'is_correct', 'selected_choice', 'created_at')
    list_display = ('user', 'question', 'is_correct', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'quiz', 'question', 'selected_choice', 'is_correct')}),
    )
