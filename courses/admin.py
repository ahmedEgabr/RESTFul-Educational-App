from django.contrib import admin
from alteby.admin_sites import main_admin
from django.db import transaction
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from courses.models import (
Course, CoursePrivacy,
CourseAttachement,
LectureAttachement,
Lecture, LecturePrivacy,
CourseActivity,
Comment,
Feedback,
CorrectInfo,
Report,
Reference,
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

main_admin.register(Note)
main_admin.register(QuizResult)
main_admin.register(QuizAttempt)
main_admin.register(Unit)
main_admin.register(Topic)
main_admin.register(LectureQuality)

class UnitTopicsInline(NestedStackedInline):
    model = Topic
    can_delete = True
    extra = 1
    verbose_name_plural = 'Topics'
    fk_name = 'unit'
    readonly_fields = ('created_by', 'updated_by')

class CourseUnitsInline(NestedStackedInline):
    model = Unit
    can_delete = True
    extra = 2
    verbose_name_plural = 'Units'
    fk_name = 'course'
    inlines = [UnitTopicsInline]
    readonly_fields = ('created_by', 'updated_by')

class CoursePrivacyInline(NestedStackedInline):
    model = CoursePrivacy
    can_delete = False
    verbose_name_plural = 'Privacy'
    fk_name = 'course'
    readonly_fields = ('created_by', 'updated_by')


class CourseAttachementsInline(NestedStackedInline):
    model = CourseAttachement
    can_delete = True
    verbose_name_plural = 'Attachements'
    fk_name = 'course'
    readonly_fields = ('created_by', 'updated_by')

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
    can_delete = True
    verbose_name_plural = 'Attachements'
    fk_name = 'lecture'
    readonly_fields = ('created_by', 'updated_by')

class LecturePrivacyInline(NestedStackedInline):
    model = LecturePrivacy
    can_delete = False
    verbose_name_plural = 'Privacy'
    fk_name = 'lecture'
    readonly_fields = ('created_by', 'updated_by')

class LectureConfig(NestedModelAdmin):
    model = Lecture

    list_filter = ('topic', 'date_created')
    list_display = ('topic', 'title')
    readonly_fields = ('duration', 'audio', 'created_by', 'updated_by')

    fieldsets = (
        ("Lecture Information", {
        'fields': (
                    'title',
                    'description',
                    'topic',
                    'video',
                    'audio',
                    'text',
                    'duration',
                    'order',
                    'quiz',
                    'teacher',
                    'references',
                    'created_by',
                    'updated_by')
                }),
    )

    inlines = [LecturePrivacyInline, LectureAttachementsInline]

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
main_admin.register(CourseActivity)

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


class RefrenceConfig(admin.ModelAdmin):
    model = Reference

    list_filter = ('categories', 'created_by', 'created_at')
    ordering = ('-created_at',)
    list_display = ('name', 'type')
    readonly_fields = ('created_by', 'updated_by', 'created_at')

main_admin.register(Reference, RefrenceConfig)
