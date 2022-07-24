from django.contrib import admin
from alteby.admin_sites import main_admin
from django.db import transaction
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from .admin_forms import LectureForm
from courses.models import (
Course, CoursePrivacy,
CourseAttachement,
LectureAttachement,
LectureExternalLink,
Lecture, LecturePrivacy,
CourseActivity,
Reference,
Comment,
Feedback,
CorrectInfo,
Report,
Feedback,
Quiz,
Question,
Choice,
QuizResult,
QuizAttempt,
Unit,
Topic,
LectureQuality,
Note
)
from .tasks import detect_and_convert_lecture_qualities, extract_and_set_lecture_audio


class NoteConfig(admin.ModelAdmin):
    model = Note
    list_filter = ('user', 'lecture')
    list_display = ('user', 'lecture')

    fieldsets = (
        (None, {'fields': ('user', 'lecture', 'note')}),
    )

main_admin.register(Note, NoteConfig)
main_admin.register(QuizResult)
main_admin.register(QuizAttempt)
main_admin.register(Unit)
main_admin.register(Topic)
main_admin.register(Reference)

class LectureQualityConfig(admin.ModelAdmin):
    model = LectureQuality

    list_filter = ('lecture',)
    list_display = ('lecture', 'get_quality_display')

    fieldsets = (
        (None, {'fields': ('lecture', 'video', 'quality')}),
    )

main_admin.register(LectureQuality, LectureQualityConfig)

class UnitTopicsInline(NestedStackedInline):
    model = Topic
    exclude = ['created_by', 'updated_by']
    can_delete = True
    extra = 1
    verbose_name_plural = 'Topics'
    fk_name = 'unit'
    list_select_related = ['unit']


class CourseUnitsInline(NestedStackedInline):
    model = Unit
    exclude = ['created_by', 'updated_by']
    can_delete = True
    extra = 2
    verbose_name_plural = 'Units'
    fk_name = 'course'
    inlines = [UnitTopicsInline]

    def get_queryset(self, request):
        qs = super(CourseUnitsInline, self).get_queryset(request)
        return qs.select_related("course")


class CoursePrivacyInline(NestedStackedInline):
    model = CoursePrivacy
    exclude = ['created_by', 'updated_by']
    can_delete = False
    verbose_name_plural = 'Privacy'
    fk_name = 'course'

    def get_queryset(self, request):
        qs = super(CoursePrivacyInline, self).get_queryset(request)
        return qs.select_related("course")


class CourseAttachementsInline(NestedStackedInline):
    model = CourseAttachement
    exclude = ['created_by', 'updated_by']
    can_delete = True
    extra = 1
    verbose_name_plural = 'Attachements'
    fk_name = 'course'

    def get_queryset(self, request):
        qs = super(CourseAttachementsInline, self).get_queryset(request)
        return qs.select_related("course")


class CourseConfig(NestedModelAdmin):
    model = Course

    list_filter = ('categories', 'date_created')
    ordering = ('-date_created',)
    list_display = ('title', 'date_created')
    readonly_fields = ('created_by', 'updated_by')

    fieldsets = (
        ("Course Information", {'fields': ('image', 'title', 'description', 'price', 'categories', 'tags', 'featured', 'quiz', 'created_by', 'updated_by')}),
    )


    @transaction.atomic
    def save_formset(self, request, form, formset, change):
        try:
            super().save_formset(request, form, formset, change)
        except Exception as e:
            print(e)
            pass

    inlines = [CoursePrivacyInline, CourseAttachementsInline, CourseUnitsInline]


main_admin.register(Course, CourseConfig)

class LectureAttachementsInline(NestedStackedInline):
    model = LectureAttachement
    exclude = ['created_by', 'updated_by']
    can_delete = True
    extra = 1
    verbose_name_plural = 'Attachements'
    fk_name = 'lecture'

    def get_queryset(self, request):
        qs = super(LectureAttachementsInline, self).get_queryset(request)
        return qs.select_related("lecture")

class LecturePrivacyInline(NestedStackedInline):
    model = LecturePrivacy
    exclude = ['created_by', 'updated_by']
    can_delete = False
    verbose_name_plural = 'Privacy'
    fk_name = 'lecture'

    def get_queryset(self, request):
        qs = super(LecturePrivacyInline, self).get_queryset(request)
        return qs.select_related("lecture")


class LectureExternalLinkInline(NestedStackedInline):
    model = LectureExternalLink
    exclude = ['created_by', 'updated_by']
    can_delete = True
    extra = 1
    verbose_name_plural = 'External Links'
    fk_name = 'lecture'

    def get_queryset(self, request):
        qs = super(LectureExternalLinkInline, self).get_queryset(request)
        return qs.select_related("lecture")


class LectureConfig(NestedModelAdmin):
    model = Lecture
    form = LectureForm
    list_filter = ('topic', 'date_created')
    list_display = ('topic', 'title')
    readonly_fields = ('duration', 'audio', 'created_by', 'updated_by')

    inlines = [LecturePrivacyInline, LectureAttachementsInline, LectureExternalLinkInline]

    def save_model(self, request, new_lecture, form, change):
        # Update lecture duration
        video_changed = False
        if not change:
            super().save_model(request, new_lecture, form, change)
            new_lecture.detect_and_change_video_duration()
            transaction.on_commit(lambda: extract_and_set_lecture_audio.delay(new_lecture.id))
            transaction.on_commit(lambda: detect_and_convert_lecture_qualities.delay(new_lecture.id))

            return new_lecture

        old_lecture = Lecture.objects.get(pk=new_lecture.pk) if new_lecture.pk else None
        super().save_model(request, new_lecture, form, change)

        if not new_lecture.video:
            new_lecture.reset_duration()
            new_lecture.reset_audio()
            video_changed = True

        elif not old_lecture or (old_lecture and old_lecture.video != new_lecture.video):
            new_lecture.detect_and_change_video_duration()
            transaction.on_commit(lambda: extract_and_set_lecture_audio.delay(new_lecture.id))
            transaction.on_commit(lambda: detect_and_convert_lecture_qualities.delay(new_lecture.id))
            video_changed = True

        if video_changed:
            new_lecture.topic.unit.course.delete_course_activity()
            new_lecture.delete_qualities()

        return new_lecture

main_admin.register(Lecture, LectureConfig)

class CourseActivityConfig(admin.ModelAdmin):
    model = CourseActivity
    list_filter = ('user', 'course', 'lecture', 'is_finished')
    ordering = ('-created_at',)
    list_display = ('user', 'course', 'lecture', 'is_finished')

    fieldsets = (
        (None, {'fields': ('user', 'course', 'lecture', 'left_off_at', 'is_finished')}),
    )

main_admin.register(CourseActivity, CourseActivityConfig)

class CommentConfig(NestedModelAdmin):
    model = Comment

    list_filter = ('user', 'object_type', 'created_at', 'status')
    list_display = ('user', 'object_type', 'created_at', 'status')

    fieldsets = (
        ("Comment Information", {'fields': ('user', 'object_type', 'object_id', 'comment_body', 'status')}),
    )

main_admin.register(Comment, CommentConfig)

class FeedbackConfig(NestedModelAdmin):
    model = Feedback

    list_filter = ('user', 'course', 'rating' ,'date_created')
    list_display = ('user', 'course', 'rating', 'date_created')

    list_display_links = ['user', 'course']

    fieldsets = (
        ("Feedback Information", {'fields': ('user', 'course', 'rating', 'description')}),
    )

main_admin.register(Feedback, FeedbackConfig)
main_admin.register(CorrectInfo)
main_admin.register(Report)



class ChoiceInline(NestedStackedInline):
    model = Choice
    can_delete = True
    verbose_name_plural = 'Choices'
    fk_name = 'question'


class QuestionInline(NestedStackedInline):
    model = Question
    extra = 1
    can_delete = True
    verbose_name_plural = 'Questions'
    fk_name = 'quiz'
    inlines = [ChoiceInline]


class QuizConfig(NestedModelAdmin):
    model = Quiz
    inlines = [QuestionInline]

main_admin.register(Quiz, QuizConfig)
