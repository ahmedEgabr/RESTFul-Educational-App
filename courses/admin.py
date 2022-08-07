from django.contrib import admin, messages
from django.shortcuts import redirect
from django import forms
from alteby.admin_sites import main_admin
from django.db import transaction
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from .admin_forms import LectureForm, CoursePlanPriceForm
from courses.models import (
Course, CoursePrivacy,
CourseAttachement,
LectureAttachement,
LectureExternalLink,
Lecture, LecturePrivacy,
CourseActivity,
Reference,
Discussion,
Reply,
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
Note,
CoursePricingPlan,
CoursePlanPrice,
Privacy
)
from .tasks import detect_and_convert_lecture_qualities, extract_and_set_lecture_audio

main_admin.register(QuizResult)
main_admin.register(QuizAttempt)
main_admin.register(Unit)
main_admin.register(Topic)
main_admin.register(Reference)
main_admin.register(CorrectInfo)
main_admin.register(Report)


@admin.register(Note, site=main_admin)
class NoteConfig(admin.ModelAdmin):
    model = Note
    list_filter = ('user', 'lecture')
    list_display = ('user', 'lecture')

    fieldsets = (
        (None, {'fields': ('user', 'lecture', 'note')}),
    )


@admin.register(LectureQuality, site=main_admin)
class LectureQualityConfig(admin.ModelAdmin):
    model = LectureQuality

    list_filter = ('lecture',)
    list_display = ('lecture', 'get_quality_display')

    fieldsets = (
        (None, {'fields': ('lecture', 'video', 'quality')}),
    )


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
    fields = (
    'option',
    'shared_with',
    'period',
    'period_type',
    'available_from',
    'enrollment_period',
    'enrollment_period_type',
    'is_downloadable',
    'is_downloadable_for_enrolled_users_only',
    'is_quiz_available',
    'is_quiz_available_for_enrolled_users_only',
    'is_attachements_available',
    "is_attachements_available_for_enrolled_users_only"
    )
    exclude = ['created_by', 'updated_by']
    can_delete = False
    verbose_name_plural = 'Privacy'
    fk_name = 'course'
    max_num = 1

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

class CoursePlanPriceFormsetBase(forms.models.BaseInlineFormSet):
    def clean(self):
        super(CoursePlanPriceFormsetBase, self).clean()
        if not self.instance.is_free_for_all_countries:
            initial_num = len(list(filter(lambda f: not self._should_delete_form(f), self.initial_forms)))
            extra_num = len(list(filter(lambda f: f.has_changed() and not self._should_delete_form(f), self.extra_forms)))
            if initial_num + extra_num < 1:
                raise forms.ValidationError("Pricing plan must has at least one price.")


CoursePlanPriceFormset = forms.models.inlineformset_factory(
CoursePricingPlan, CoursePlanPrice, formset=CoursePlanPriceFormsetBase, form=CoursePlanPriceForm
)

class CoursePlanPriceInline(admin.StackedInline):
    model = CoursePlanPrice
    can_delete = True
    extra = 0
    verbose_name_plural = 'Prices'
    fk_name = 'plan'
    formset = CoursePlanPriceFormset
    fieldsets = (
        (None, {
        'fields': (
        (
            'amount',
            'currency'
        ),
        'countries', 
        'select_all_countries',
        'is_free_for_selected_countries',
        'is_default',
        'is_active'
        )}),
    )
    def get_queryset(self, request):
        qs = super(CoursePlanPriceInline, self).get_queryset(request)
        return qs.select_related("plan")


@admin.register(CoursePricingPlan, site=main_admin)
class CoursePricingPlanConfig(admin.ModelAdmin):
    model = CoursePricingPlan

    list_filter = ('course', 'duration', 'duration_type', 'lifetime_access', 'is_default', 'is_active', 'created_at')
    ordering = ('-created_at',)
    list_display = ('course', 'duration', 'duration_type', 'lifetime_access', 'is_default', 'is_active', 'created_at')
    readonly_fields = ('created_by', 'updated_by')

    change_form_template = 'admin/forms/pricing_plan_change_form.html'

    fieldsets = (
        (None, {
        'fields': (
        'course',
        (
            'duration',
            'duration_type'
        ),
        'lifetime_access',
        'is_free_for_all_countries',
        'is_default',
        'is_active'
        )}),
    )
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):

        return super(CoursePricingPlanConfig, self).render_change_form(
            request, context, add, change, form_url, obj)

    inlines = [CoursePlanPriceInline]


@admin.register(Course, site=main_admin)
class CourseConfig(NestedModelAdmin):
    model = Course

    list_filter = ('categories', 'language', 'created_by', 'updated_by', 'date_created')
    ordering = ('-date_created',)
    list_display = ('title', 'date_created')
    readonly_fields = ('is_free', 'created_by', 'updated_by')
    inlines = [CoursePrivacyInline, CourseAttachementsInline, CourseUnitsInline]
    fieldsets = (
        ("Course Information", {
        'fields': (
        'image',
        'title',
        'description',
        'objectives',
        'about',
        'language',
        'categories',
        'tags',
        'featured',
        'is_free',
        'created_by',
        'updated_by'
        )}),
    )
    
    change_form_template = 'admin/forms/course_change_form.html'


    @transaction.atomic
    def save_formset(self, request, form, formset, change):
        try:
            super().save_formset(request, form, formset, change)
        except Exception as e:
            print(e)
            pass

    def save_model(self, request, obj, form, change):
        if not obj.id or not obj.pricing_plans.all():
            messages.success(
            request,
            "Course saved successfully!"
            )
            messages.warning(
            request,
            "You have to add course plan and prices or the course will be free by default."
            )
        super(CourseConfig, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        url = reverse('admin:%s_%s_add' % ("courses",  "coursepricingplan"))
        return redirect(url)
    
    def response_change(self, request, obj):
        if not obj.pricing_plans.all():
            url = reverse('admin:%s_%s_add' % ("courses",  "coursepricingplan"))
            return redirect(url)
        return super(CourseConfig, self).response_change(request, obj)


class LectureAttachementsInline(admin.StackedInline):
    model = LectureAttachement
    exclude = ['created_by', 'updated_by']
    can_delete = True
    extra = 1
    verbose_name_plural = 'Attachements'
    fk_name = 'lecture'

    def get_queryset(self, request):
        qs = super(LectureAttachementsInline, self).get_queryset(request)
        return qs.select_related("lecture")

class LecturePrivacyInline(admin.StackedInline):
    model = LecturePrivacy
    fields = (
    'option',
    'shared_with',
    # 'period',
    # 'period_type',
    # 'available_from',
    # 'enrollment_period',
    # 'enrollment_period_type',
    'is_downloadable',
    'is_downloadable_for_enrolled_users_only',
    'is_quiz_available',
    'is_quiz_available_for_enrolled_users_only',
    'is_attachements_available',
    "is_attachements_available_for_enrolled_users_only"
    )
    exclude = ['created_by', 'updated_by']
    can_delete = False
    verbose_name_plural = 'Privacy'
    fk_name = 'lecture'
    max_num = 1


    def get_queryset(self, request):
        qs = super(LecturePrivacyInline, self).get_queryset(request)
        return qs.select_related("lecture")


class LectureExternalLinkInline(admin.StackedInline):
    model = LectureExternalLink
    exclude = ['created_by', 'updated_by']
    can_delete = True
    extra = 1
    verbose_name_plural = 'External Links'
    fk_name = 'lecture'

    def get_queryset(self, request):
        qs = super(LectureExternalLinkInline, self).get_queryset(request)
        return qs.select_related("lecture")


@admin.register(Lecture, site=main_admin)
class LectureConfig(admin.ModelAdmin):
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


@admin.register(CourseActivity, site=main_admin)
class CourseActivityConfig(admin.ModelAdmin):
    model = CourseActivity
    list_filter = ('user', 'course', 'lecture', 'is_finished')
    ordering = ('-created_at',)
    list_display = ('user', 'course', 'lecture', 'is_finished')

    fieldsets = (
        (None, {'fields': ('user', 'course', 'lecture', 'left_off_at', 'is_finished')}),
    )


class ReplyInline(admin.StackedInline):
    model = Reply
    exclude = ['updated_by']
    readonly_fields = ["created_by"]
    can_delete = True
    extra = 1
    verbose_name_plural = 'Replies'
    fk_name = 'discussion'


@admin.register(Discussion, site=main_admin)
class DiscussionConfig(admin.ModelAdmin):
    model = Discussion

    list_filter = ('user', 'course', 'topic', 'lecture', 'created_at', 'status')
    list_display = ('user', 'course', 'topic', 'lecture', 'created_at', 'status')

    fieldsets = (
        ("Discussion Information", {'fields': ('user', 'course', 'topic', 'lecture', 'body', 'status')}),
    )

    inlines = (ReplyInline,)


@admin.register(Feedback, site=main_admin)
class FeedbackConfig(NestedModelAdmin):
    model = Feedback

    list_filter = ('user', 'course', 'rating' ,'date_created')
    list_display = ('user', 'course', 'rating', 'date_created')

    list_display_links = ['user', 'course']

    fieldsets = (
        ("Feedback Information", {'fields': ('user', 'course', 'rating', 'description')}),
    )


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


@admin.register(Quiz, site=main_admin)
class QuizConfig(NestedModelAdmin):
    model = Quiz
    inlines = [QuestionInline]
