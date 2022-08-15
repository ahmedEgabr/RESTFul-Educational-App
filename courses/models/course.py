from django.utils import timezone
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.contenttypes.models import ContentType
from main.utility_models import UserActionModel, TimeStampedModel
from courses.managers import CustomCourseManager
from courses.models.discussion import Discussion
from courses.models.abstract_privacy import Privacy
from courses.models.lecture import Lecture
from courses.models.topic import Topic
from courses.models.course_privacy import CoursePrivacy
from courses.models.activity import CourseActivity
from courses.models.reference import Reference
from courses.models.course_pricing_plan import CoursePricingPlan
from courses.models.course_plan_price import CoursePlanPrice
from users.models import User, Teacher
from main.utility_models import Languages
from payment.models import CourseEnrollment


class Course(UserActionModel):

    title = models.CharField(max_length=100)
    description = RichTextField()
    objectives = RichTextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField("categories.Category", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to="courses/images", blank=True)
    tags = models.ManyToManyField("categories.Tag", blank=True)
    language = models.CharField(choices=Languages.choices, default=Languages.arabic, max_length=20)
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)

    objects = CustomCourseManager()

    def __str__(self):
          return self.title

    def atomic_post_save(self, sender, created, **kwargs):
        if not hasattr(self, "privacy"):
            self.__class__.create_privacy(self)

    @classmethod
    def create_privacy(cls, course):
        return CoursePrivacy.objects.get_or_create(course=course)

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


    def delete_course_activity(self):
        CourseActivity.objects.filter(course=self).delete()
        return True

    def get_units_count(self):
        return self.units.count()

    def get_lectures_count(self):
        return self.units.aggregate(count=models.Count('topics__lectures'))['count']

    def get_lectures_duration(self):
        duration = self.units.aggregate(sum=models.Sum('topics__lectures__duration'))['sum']
        if not duration:
            duration = 0
        return duration

    def is_finished(self, user):
        lectures = Lecture.objects.filter(topic__unit__course=self)
        if not lectures:
            return False
        activity = self.activity.filter(user=user, lecture__in=lectures).count()
        return len(lectures) == activity

    def get_lectures(self):
        course_units_ids = self.units.values_list('id', flat=True)
        course_topics_ids = Topic.objects.filter(unit__in=course_units_ids).values_list('id', flat=True)
        lectures = Lecture.objects.filter(topic__in=course_topics_ids)
        return lectures

    def get_contributed_teachers(self):
        teachers_ids_list = self.get_lectures().values_list("teacher", flat=True)
        teachers_list = Teacher.objects.filter(user_id__in=teachers_ids_list)
        return teachers_list

    @property
    def references(self):
        references_ids = self.get_lectures().filter(~models.Q(references=None)).values_list("references__id", flat=True)
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
            created = CourseEnrollment.objects.create(
                user=user,
                course=self,
                payment_type=CourseEnrollment.PAYMENT_TYPES.free,
                enrollment_duration=self.privacy.enrollment_duration,
                enrollment_duration_type=self.privacy.enrollment_duration_type
            )
        else:
            created = CourseEnrollment.objects.create(
                user=user,
                course=self,
                payment_type=CourseEnrollment.PAYMENT_TYPES.free,
                lifetime_enrollment=True
            )
        
        if not created:
            return False
        return True
        