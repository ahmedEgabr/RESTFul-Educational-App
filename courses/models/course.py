from django.utils import timezone
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.contenttypes.models import ContentType
from courses.models.abstract_privacy import Privacy
from courses.models.activity import CourseActivity
from main.utility_models import UserActionModel
from courses.managers import CustomCourseManager
from courses.models.discussion import Discussion
from courses.models.lecture import Lecture
from courses.models.course_privacy import CoursePrivacy
from courses.models.reference import Reference
from courses.models.course_pricing_plan import CoursePricingPlan
from courses.models.course_plan_price import CoursePlanPrice
from users.models import User, Teacher
from main.utility_models import Languages
from payment.models import CourseEnrollment


class Course(UserActionModel):

    title = models.CharField(max_length=100)
    description = RichTextField(blank=True, null=True)
    objectives = RichTextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField("categories.Category", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to="courses/images", blank=True)
    tags = models.ManyToManyField("categories.Tag", blank=True)
    language = models.CharField(choices=Languages.choices, default=Languages.arabic, max_length=20)
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    objects = CustomCourseManager()

    def __str__(self):
          return self.title

    def atomic_post_save(self, sender, created, **kwargs):
        if not hasattr(self, "privacy"):
            self.create_privacy()

    def create_privacy(self):
        course_privacy_settings, created = CoursePrivacy.objects.get_or_create(course=self)
        return course_privacy_settings

    def is_allowed_to_access_course(self, user):
        if not isinstance(user, User):
            return False
        access_granted = self.check_privacy(user)
        if access_granted or self.is_enrolled(user=user):
            return True
        return False

    def check_privacy(self, user):
        if not hasattr(self, "privacy"):
            return False
        
        elif self.privacy.is_private:
            return False
        
        elif self.privacy.is_public:
            return True
        
        elif self.privacy.is_shared:
            return user in self.privacy.shared_with.all()
        
        elif self.privacy.is_public_for_limited_duration:
            return self.privacy.is_available_during_limited_duration
        
        return False

    def get_units_count(self):
        return self.units.count()

    def get_lectures(self):
        lectures_ids = self.units.filter(
            ~models.Q(topics__assigned_lectures=None)
            ).values_list(
                "topics__assigned_lectures__lecture", 
                flat=True
        )            
        lectures_queryset = Lecture.objects.filter(id__in=lectures_ids)
        return lectures_queryset, lectures_ids
    
    def get_lectures_count(self):
        return self.units.aggregate(count=models.Count('topics__assigned_lectures'))['count']

    def get_lectures_duration(self):
        duration = self.units.aggregate(sum=models.Sum('topics__assigned_lectures__lecture__duration'))['sum']
        if not duration:
            duration = 0
        return duration

    def get_lectures_viewed(self, user):
        lectures_viewd_count = 0
        lectures_queryset, lectures_ids = self.get_lectures()
        lectures_viewed = CourseActivity.objects.filter(lecture__id__in=lectures_ids, user=user)
        for lecture_activity in lectures_viewed:
            lectures_viewd_count += list(lectures_ids).count(lecture_activity.lecture.id)
        return lectures_viewd_count

    def is_finished(self, user):
        lectures_viewed_count = self.get_lectures_viewed(user=user)
        return self.get_lectures_count() == lectures_viewed_count
    
    def get_contributed_teachers(self):
        lectures_queryset, lectures_ids = self.get_lectures()
        teachers_ids_list = lectures_queryset.values_list("teacher", flat=True)
        teachers_list = Teacher.objects.filter(user_id__in=teachers_ids_list)
        return teachers_list

    @property
    def references(self):
        lectures_queryset, lectures_ids = self.get_lectures()
        references_ids = lectures_queryset.filter(~models.Q(references=None)).values_list("references__id", flat=True)
        if not references_ids:
            return None
        return Reference.objects.filter(id__in=list(references_ids))

    @property
    def discussions(self):
        return Discussion.objects.filter(object_type=ContentType.objects.get_for_model(self).id, status='approved')

    @property
    def has_pricing_plans(self):
        return self.pricing_plans.exists()

    def create_default_pricing_plan(self):
        return CoursePricingPlan.create_default_pricing_plan(course=self)
    
    def get_pricing_plans(self, request):

        queryset = self.pricing_plans
        if not queryset.exists():
            return []
        
        country_regex = u'^{0},|,{0},|,{0}$|^{0}$'.format(request.country)
        
        prices_filter_queryset = CoursePlanPrice.objects.filter(
            models.Q(countries__regex=country_regex) |
            models.Q(select_all_countries=True) | 
            (models.Q(is_free_for_selected_countries=True) & models.Q(countries__regex=country_regex)),
            plan__course=self,
            is_active=True
            ).order_by("amount")
        
        default_prices_filter = CoursePlanPrice.objects.filter(
            plan__course=self,
            is_default=True, 
            is_active=True
            ) 
        
        queryset = queryset.prefetch_related(
            models.Prefetch("prices", queryset=prices_filter_queryset if prices_filter_queryset else default_prices_filter)
        )
        
        pricing_plans = queryset.filter(
            models.Q(is_free_for_all_countries=True) | (
                models.Q(prices__countries__regex=country_regex) & 
                models.Q(prices__is_free_for_selected_countries=True) &
                models.Q(prices__is_active=True) |
                models.Q(prices__countries__regex=country_regex)
            ),
            is_active=True,
            is_default=False,
            ).distinct()
        if not pricing_plans:
            pricing_plans = queryset.filter(is_default=True, is_active=True) 
        return pricing_plans
    
    def get_default_pricing_plan(self, request):
        
        queryset = self.pricing_plans
        if not queryset.exists():
            return None
        
        country_regex = u'^{0},|,{0},|,{0}$|^{0}$'.format(request.country)
        
        prices_filter_queryset = CoursePlanPrice.objects.filter(
            models.Q(countries__regex=country_regex) |
            models.Q(select_all_countries=True) | 
            (models.Q(is_free_for_selected_countries=True) & models.Q(countries__regex=country_regex)),
            plan__course=self,
            is_active=True
            ).order_by("amount")

        default_prices_filter = CoursePlanPrice.objects.filter(
            plan__course=self,
            is_default=True,
            is_active=True
            ) 
        
        queryset = queryset.prefetch_related(
            models.Prefetch("prices", queryset=prices_filter_queryset if prices_filter_queryset else  default_prices_filter)
        )
        
        # Check for free plans  available for request country
        pricing_plan = queryset.filter(
            models.Q(is_free_for_all_countries=True) | (
                models.Q(prices__countries__regex=country_regex) & 
                models.Q(prices__is_free_for_selected_countries=True) &
                models.Q(prices__is_active=True) |
                models.Q(prices__countries__regex=country_regex)
            ),
            is_active=True
            ).first()
        
        if not pricing_plan:
            pricing_plan = queryset.filter(is_active=True, is_default=True).first()
        return pricing_plan
    
    def is_enrolled(self, user):
        return CourseEnrollment.objects.filter(
            models.Q(lifetime_enrollment=True) |
            models.Q(expiry_date__gt=timezone.now()),
            course=self, 
            user=user,
            force_expiry=False,
            is_active=True
            ).exists()
    
    def enroll(self, user):
        if not isinstance(user, User):
            return False
        
        if self.is_enrolled(user=user):
            return True
        
        if self.privacy.is_public_for_limited_duration:
            CourseEnrollment.objects.create(
                user=user,
                course=self,
                payment_type=CourseEnrollment.PAYMENT_TYPES.FREE,
                enrollment_duration=self.privacy.enrollment_duration,
                enrollment_duration_type=self.privacy.enrollment_duration_type
            )
        return True
    
    @classmethod
    def get_allowed_courses(cls, user):
        return Course.objects.exclude(
            models.Q(privacy__option=Privacy.PRIVACY_CHOICES.shared) &
            ~models.Q(privacy__shared_with__in=[user]) &
            ~(
                (
                    models.Q(enrollments__lifetime_enrollment=True) |
                    models.Q(enrollments__expiry_date__gt=timezone.now())
                ) & 
                models.Q(enrollments__user=user) &
                models.Q(enrollments__force_expiry=False) &
                models.Q(enrollments__is_active=True) |
                models.Q(is_active=True)
            )
            
        )
        