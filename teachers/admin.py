import nested_admin
from django.utils.formats import date_format
from django.utils import timezone
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from alteby.admin_sites import teacher_admin
from courses.admin import (
CourseConfig, CoursePricingPlanConfig,
LectureAttachementsInline, LecturePrivacyInline, LectureExternalLinkInline, ReplyInline, LectureOverlapInline
)
from courses.models import Course, Lecture, Discussion, Reference, CoursePricingPlan
from categories.models import Tag, Category, ReferenceCategory
from .admin_forms import LectureForm, ReferenceForm, LectureOverlapForm
from payment.models import CourseEnrollment
from payment.admin import CourseEnrollmentConfig
from .admin_forms import LectureForm, CoursePricingPlanForm
from courses.tasks import detect_and_convert_lecture_qualities, extract_and_set_lecture_audio



class LectureOverlapInlineForTeacher(LectureOverlapInline):
    form = LectureOverlapForm
    
@admin.register(CoursePricingPlan, site=teacher_admin)
class TeacherCoursePricingPlanConfig(CoursePricingPlanConfig):
    form = CoursePricingPlanForm
    
    def get_queryset(self, request):
        qs = super(TeacherCoursePricingPlanConfig, self).get_queryset(request)
        return qs.select_related("course").filter(
            Q(created_by=request.user) |
            Q(course__created_by=request.user)
            )

@admin.register(Course, site=teacher_admin)
class TeacherCourseConfig(CourseConfig):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    def response_add(self, request, obj, post_url_continue=None):
        url = reverse('teacher_admin:%s_%s_add' % ("courses",  "coursepricingplan"))
        return redirect(url)
    
    def response_change(self, request, obj):
        if not obj.pricing_plans.all():
            url = reverse('teacher_admin:%s_%s_add' % ("courses",  "coursepricingplan"))
            return redirect(url)
        return super(CourseConfig, self).response_change(request, obj)

@admin.register(Lecture, site=teacher_admin)
class LectureConfig(nested_admin.NestedModelAdmin):
    model = Lecture
    form = LectureForm

    list_filter = ('topic', 'date_created')
    list_display = ('topic', 'title')
    readonly_fields = ('duration', 'audio', 'created_by', 'updated_by')

    inlines = [LecturePrivacyInline, LectureAttachementsInline, LectureExternalLinkInline, LectureOverlapInlineForTeacher]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return request.user.lectures_created.all()

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
            new_lecture.delete_activity_for_all_users()
            new_lecture.delete_qualities()

        return new_lecture


@admin.register(CourseEnrollment, site=teacher_admin)
class CourseEnrollmentConfig(CourseEnrollmentConfig):
    model = CourseEnrollment
    change_form_template = 'admin/forms/course_enrollment_change_form.html'
    
    readonly_fields = (
    'user',
    'course',
    'payment_method',
    'payment_type',
    'enrollment_duration',
    'enrollment_duration_type',
    'lifetime_enrollment',
    'enrollment_date',
    'expiry_date',
    'force_expiry',
    'is_active'
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return request.user.courses_created.all()
    
    @staticmethod
    def expiry_date(object):
        if not object.calculate_expiry_date:
            return None
        return date_format(timezone.localtime(object.calculate_expiry_date), 'DATETIME_FORMAT')


@admin.register(Discussion, site=teacher_admin)
class DiscussionConfig(admin.ModelAdmin):
    model = Discussion

    list_filter = ('user', 'course', 'topic', 'lecture', 'created_at', 'status')
    list_display = ('user', 'course', 'topic', 'lecture', 'created_at', 'status')
    readonly_fields = ("user", "course", "topic", "lecture", "body")
    fieldsets = (
        ("Discussion Information", {'fields': ('user', 'body', 'course', 'topic', 'lecture', 'status')}),
    )

    def get_queryset(self, request):
        courses = request.user.created_courses.all()
        if not courses:
            courses = []
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(course__in=courses)

    inlines = (ReplyInline,)


@admin.register(Tag, site=teacher_admin)
class TagConfig(admin.ModelAdmin):
    model = Tag

    list_filter = ('name', 'created_at',)
    ordering = ('-created_at',)
    list_display = ('name', 'created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {'fields': ('name', 'created_at')}),
    )

@admin.register(Category, site=teacher_admin)
class CategoryConfig(admin.ModelAdmin):
    model = Category

    list_filter = ('name', 'created_at',)
    ordering = ('-created_at',)
    list_display = ('name', 'created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {'fields': ('name', 'created_at')}),
    )


@admin.register(Reference, site=teacher_admin)
class ReferenceConfig(admin.ModelAdmin):
    model = Reference
    form = ReferenceForm

    list_filter = ('name', 'type', 'categories', 'created_at',)
    ordering = ('-created_at',)
    list_display = ('name', 'type', 'created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {'fields': ('name', 'type', 'link', 'categories', 'created_at')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

@admin.register(ReferenceCategory, site=teacher_admin)
class ReferenceCategoryConfig(admin.ModelAdmin):
    model = ReferenceCategory

    list_filter = ('name', 'created_at',)
    ordering = ('-created_at',)
    list_display = ('name', 'created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {'fields': ('name', 'created_at')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
