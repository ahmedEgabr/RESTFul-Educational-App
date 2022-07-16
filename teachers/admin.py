from django.contrib import admin
from nested_inline.admin import NestedModelAdmin
from django.db import transaction
from alteby.admin_sites import teacher_admin
from courses.admin import (
UnitTopicsInline, CourseUnitsInline, CoursePrivacyInline, CourseAttachementsInline,
LectureAttachementsInline, LecturePrivacyInline
)
from courses.models import Course, Lecture
from .admin_forms import LectureForm, CourseEnrollmentForm
from payment.models import CourseEnrollment


@admin.register(Course, site=teacher_admin)
class CourseConfig(NestedModelAdmin):
    model = Course

    list_filter = ('categories', 'date_created')
    ordering = ('-date_created',)
    list_display = ('title', 'date_created')
    readonly_fields = ('created_by', 'updated_by')

    fieldsets = (
        ("Course Information", {'fields': ('image', 'title', 'description', 'price', 'categories', 'tags', 'featured', 'quiz', 'created_by', 'updated_by')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    @transaction.atomic
    def save_formset(self, request, form, formset, change):
        try:
            super().save_formset(request, form, formset, change)
        except Exception as e:
            print(e)
            pass

    inlines = [CoursePrivacyInline, CourseAttachementsInline, CourseUnitsInline]


@admin.register(Lecture, site=teacher_admin)
class LectureConfig(NestedModelAdmin):
    model = Lecture
    form = LectureForm

    list_filter = ('topic', 'date_created')
    list_display = ('topic', 'title')
    readonly_fields = ('duration', 'audio', 'created_by', 'updated_by')

    fieldsets = (
        ("Lecture Information", {'fields': ('title', 'description', 'topic', 'video', 'audio', 'text', 'duration', 'order', 'quiz', 'teacher', 'references', 'created_by', 'updated_by')}),
    )

    inlines = [LecturePrivacyInline, LectureAttachementsInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

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


# @admin.register(CourseEnrollment, site=teacher_admin)
class CourseEnrollmentConfig(admin.ModelAdmin):
    model = CourseEnrollment
    form = CourseEnrollmentForm

    list_filter = ('user', 'course', 'payment_method', 'payment_type', 'date_created')
    ordering = ('-date_created',)
    list_display = ('user', 'course', 'payment_method', 'payment_type', 'date_created')

    fieldsets = (
        ("Course Enrollment Information", {'fields': ('user', 'course', 'payment_method', 'payment_type')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
