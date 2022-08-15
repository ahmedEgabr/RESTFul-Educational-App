from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from django_countries.serializers import CountryFieldMixin
from courses.models import (
Course, Unit, Topic,
CourseActivity,
Lecture, LectureQuality, CoursePrivacy, CoursePricingPlan, CoursePlanPrice,
LecturePrivacy,
Quiz,
Attachement, Discussion, Reply, Feedback,
LectureExternalLink, Reference
)
from alteby.utils import seconds_to_duration
from categories.api.serializers import CategorySerializer, TagSerializer
from django.db.models import Sum
from payment.models import CourseEnrollment
from users.api.serializers import TeacherSerializer, BasicUserSerializer
from question_banks.models import QuestionResult, Question, Choice


class CoursePathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title')
        
class UnitPathSerializer(serializers.ModelSerializer):
    course = CoursePathSerializer(many=False, read_only=True)
    class Meta:
        model = Lecture
        fields = ('id', 'title', 'course')
        
class TopicPathSerializer(serializers.ModelSerializer):
    unit = UnitPathSerializer(many=False, read_only=True)
    class Meta:
        model = Lecture
        fields = ('id', 'title', 'unit')
        
class LecturePathSerializer(serializers.ModelSerializer):
    topic = TopicPathSerializer(many=False, read_only=True)
    class Meta:
        model = Lecture
        fields = ('id', 'title', 'topic')
        
class LectureIndexSerialiser(serializers.ModelSerializer):

    can_access = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = ('id', 'title', 'can_access')

    def get_can_access(self, lecture):
        user = self.context.get('user', None)
        return lecture.check_privacy(user) or lecture.is_enrolled


class TopicIndexSerialiser(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['lectures'].context.update(self.context)

    lectures = LectureIndexSerialiser(many=True, read_only=True)
    class Meta:
        model = Topic
        fields = ('id', 'title', 'lectures')

class UnitIndexSerialiser(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['topics'].context.update(self.context)

    topics = TopicIndexSerialiser(many=True, read_only=True)
    class Meta:
        model = Unit
        fields = ('id', 'title', 'topics')

class CourseIndexSerialiser(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['units'].context.update(self.context)

    units = UnitIndexSerialiser(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ('id', 'title', 'units')

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class AttachementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachement
        fields = '__all__'

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ("id", "name", "type", "link")


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'choice', 'is_correct', 'explanation', 'image')

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ('id', 'title', 'choices', 'extra_info', 'image')

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    # number_of_questions = serializers.CharField(source='get_questions_count')
    class Meta:
        model = Quiz
        fields = ('id', 'name', 'description', 'questions')

class BaseQuestionResultSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False, read_only=True)
    selected_choice = ChoiceSerializer(many=False, read_only=True)
    class Meta:
        model = QuestionResult
        fields = ('id', 'question', 'selected_choice', 'is_correct')

class QuizResultSerializer(serializers.ModelSerializer):
    selected_choice = ChoiceSerializer(many=False, read_only=True)
    result = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField('get_questions_count')
    score = serializers.SerializerMethodField('get_score')
    class Meta:
        model = Quiz
        fields = ("id", "name", "description", "lecture", "questions_count", "created_at", "result", "score", "selected_choice")

    num_of_questions = 0
    num_of_right_answers = 0
    def get_result(self, quiz):
        user = self.context.get('request', None).user
        # Must select distinct, but it is not supported by SQLite
        quiz_answers = QuestionResult.objects.select_related(
            'question', 'selected_choice'
            ).prefetch_related(
                'question__choices'
                ).filter(
                    user=user, quiz=quiz
                    )
                
        self.num_of_right_answers = quiz_answers.filter(is_correct=True).count()
        return BaseQuestionResultSerializer(quiz_answers, many=True, read_only=True).data

    def get_score(self, quiz):
        return (self.num_of_right_answers/self.num_of_questions)*100

    def get_questions_count(self, quiz):
        self.num_of_questions = quiz.questions.count()
        return self.num_of_questions

class CoursePrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePrivacy
        fields =(
        "id",
        "course",
        "option",
        "available_from",
        "is_available_during_limited_duration",
        "duration",
        "duration_type",
        "enrollment_duration",
        "enrollment_duration_type",
        "is_downloadable",
        "is_downloadable_for_enrolled_users_only",
        "is_quiz_available",
        "is_quiz_available_for_enrolled_users_only",
        "is_attachements_available",
        "is_attachements_available_for_enrolled_users_only",
        "shared_with"
        )

class LecturePrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturePrivacy
        fields =(
        "id",
        "lecture",
        "option",
        # "available_from",
        # "is_available_during_limited_duration",
        # "duration",
        # "durationtype",
        # "enrollment_duration",
        # "enrollment_duration_type",
        "is_downloadable",
        "is_downloadable_for_enrolled_users_only",
        "is_quiz_available",
        "is_quiz_available_for_enrolled_users_only",
        "is_attachements_available",
        "is_attachements_available_for_enrolled_users_only",
        "shared_with"
        )

class CourseActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseActivity
        fields = '__all__'

class DemoLectureSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(many=False, read_only=True)
    viewed = serializers.BooleanField()
    left_off_at = serializers.FloatField()
    privacy = LecturePrivacySerializer(many=False, read_only=True)
    has_video = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()
    has_script = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = (
        'id',
        'title',
        'description',
        'objectives',
        'order',
        'topic',
        'path',
        'privacy',
        'teacher',
        'duration',
        'left_off_at',
        'viewed',
        'has_video',
        'has_audio',
        'has_script',
        'updated_at'
        )

    def is_viewed(self, lecture):
        user = self.context.get('request', None).user
        return lecture.activity.filter(user=user).exists()

    def get_has_video(self, lecture):
        return True if lecture.video else False

    def get_has_audio(self, lecture):
        return True if lecture.audio else False

    def get_has_script(self, lecture):
        return True if lecture.script else False
    
    from collections import OrderedDict

    def get_path(self, lecture):
        return LecturePathSerializer(lecture).data

class LectureQualitySerializer(serializers.ModelSerializer):
    quality = serializers.SerializerMethodField()
    class Meta:
        model = LectureQuality
        exclude = ('lecture', 'id')

    def get_quality(self, lecture_quality):
        return lecture_quality.get_quality_display()


class LectureExternalLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureExternalLink
        fields = "__all__"


class FullLectureSerializer(DemoLectureSerializer):
    teacher = TeacherSerializer(many=False, read_only=True)
    qualities = LectureQualitySerializer(many=True, read_only=True)
    path = serializers.SerializerMethodField()
    class Meta:
        model = Lecture
        fields = (
        'id',
        'topic',
        'title',
        'description',
        'objectives',
        'video',
        'qualities',
        'teacher',
        'audio',
        'script',
        'duration',
        'left_off_at',
        'viewed',
        'order',
        'privacy',
        'path'
        )

    def convert_duration(self, lecture):
        return seconds_to_duration(lecture.duration)

    def get_course_id(self, lecture):
        return lecture.course.id
    
    def get_path(self, lecture):
        return LecturePathSerializer(lecture).data

class QuerySerializerMixin(object):
    PREFETCH_FIELDS = [] # Here is for M2M fields
    RELATED_FIELDS = [] # Here is for ForeignKeys

    @classmethod
    def get_related_queries(cls, queryset):
        # This method we will use in our ViewSet
        # for modify queryset, based on RELATED_FIELDS and PREFETCH_FIELDS
        if cls.RELATED_FIELDS:
            queryset = queryset.select_related(*cls.RELATED_FIELDS)
        if cls.PREFETCH_FIELDS:
            queryset = queryset.prefetch_related(*cls.PREFETCH_FIELDS)
        return queryset

class TopicsListSerializer(serializers.ModelSerializer):
    lectures_count = serializers.IntegerField()
    lectures_duration = serializers.FloatField()
    is_finished = serializers.SerializerMethodField('get_activity_status')
    can_access = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields =('id', 'title', 'unit', 'path', 'lectures_count', 'lectures_duration', 'progress', 'is_finished', 'order', 'can_access')

    def get_activity_status(self, topic):
        if not topic.lectures_count:
            return False
        return topic.lectures_count == topic.num_of_lectures_viewed

    def format_lectures_duration(self, topic):
        return seconds_to_duration(topic.lectures_duration)
    
    def get_can_access(self, topic):
        user = self.context.get("request", None).user
        return topic.unit.course.is_allowed_to_access_course(user=user)
    
    def get_path(self, topic):
        return TopicPathSerializer(topic).data
    
    def get_progress(self, topic):
        return round(topic.num_of_lectures_viewed/topic.lectures_count * 100, 2)


class TopicDetailSerializer(serializers.ModelSerializer):
    lectures_count = serializers.IntegerField()
    lectures_duration = serializers.FloatField()
    progress = serializers.SerializerMethodField()
    is_finished = serializers.SerializerMethodField('get_activity_status')

    class Meta:
        model = Topic
        fields =('id', 'title', 'unit', 'lectures_count', 'lectures_duration', 'progress', 'is_finished', 'order')

    def get_activity_status(self, topic):
        if not topic.lectures_count:
            return False
        return topic.lectures_count == topic.num_of_lectures_viewed

    def format_lectures_duration(self, topic):
        return seconds_to_duration(topic.lectures_duration)
    
    def get_progress(self, topic):
        return round(topic.num_of_lectures_viewed/topic.lectures_count * 100, 2)

class UnitSerializer(serializers.ModelSerializer):
    lectures_count = serializers.IntegerField()
    lectures_duration = serializers.FloatField()
    is_finished = serializers.SerializerMethodField('get_activity_status')
    can_access = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ('id', 'title', 'course', 'order', 'path', 'lectures_duration', 'lectures_count', 'progress', 'is_finished', 'can_access')

    def get_activity_status(self, unit):
        if not unit.lectures_count:
            return False
        return unit.lectures_count == unit.num_of_lectures_viewed

    def format_lectures_duration(self, unit):
        return seconds_to_duration(unit.lectures_duration)
    
    def get_can_access(self, unit):
        user = self.context.get("request", None).user
        return unit.course.is_allowed_to_access_course(user=user)
    
    def get_progress(self, unit):
        return round(unit.num_of_lectures_viewed/unit.lectures_count * 100, 2)
     
    def get_path(self, unit):
        return UnitPathSerializer(unit).data

class UnitTopicsSerializer(serializers.ModelSerializer):
    topics = TopicsListSerializer(many=True, read_only=True)
    lectures_count = serializers.IntegerField(source='get_lectures_count')
    lectures_duration = serializers.CharField(source='get_lectures_duration')
    
    class Meta:
        model = Unit
        fields = ('id', 'title', 'course', 'order', 'topics', 'lectures_duration', 'lectures_count')
    
class CoursePlanPriceSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = CoursePlanPrice
        fields = ("id", "amount", "currency")
        
class CoursePricingPlanSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    class Meta:
        model = CoursePricingPlan
        fields = ("id", "duration", "duration_type", "lifetime_access", "is_free_for_all_countries", "price", "created_at")
    
    def get_price(self, plan):
        return CoursePlanPriceSerializer(plan.prices.first(), many=False).data


class CourseSerializer(serializers.ModelSerializer, QuerySerializerMixin):
    language = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField('get_progress')
    is_enrolled = serializers.SerializerMethodField('get_enrollment')
    units_count = serializers.IntegerField(source='get_units_count')
    lectures_count = serializers.IntegerField(source='get_lectures_count')
    course_duration = serializers.CharField(source='get_lectures_duration')

    # Flag: this field hits the DB
    is_finished = serializers.SerializerMethodField('get_activity_status')

    privacy = CoursePrivacySerializer(many=False, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    pricing_plan = serializers.SerializerMethodField()
    PREFETCH_FIELDS = ['categories__course_set', 'privacy__shared_with']


    class Meta:
        model = Course
        fields = (
        'id', 'image', 'title',
        'description', 'objectives', 'about',
        'categories', 'tags', 'language',
        'privacy', 
        'pricing_plan',
        'units_count', 
        'lectures_count', 
        'course_duration', 
        'progress', 
        'is_enrolled', 
        'is_finished', 
        'is_free', 
        'date_created'
        )

    def get_progress(self, course):
         user = self.context.get('request', None).user
         content_viewed_count = course.activity.filter(user=user).count()

         content_count = course.get_lectures_count()
         if not content_count:
             return 0.0
         return content_viewed_count/content_count*100

    def get_enrollment(self, course):
         user = self.context.get('request', None).user
         return course.is_enrolled(user=user)

    def get_activity_status(self, course):
        user = self.context.get('request', None).user
        return course.is_finished(user)

    def format_lectures_duration(self, course):
        return seconds_to_duration(course.course_duration)

    def get_language(self, course):
        return course.get_language_display()

    def get_pricing_plan(self, course):
        request = self.context.get('request', None)
        pricing_plan = course.get_default_pricing_plan(request)
        if not pricing_plan:
            return None
        return CoursePricingPlanSerializer(pricing_plan, many=False).data


class CoursesSerializer(serializers.ModelSerializer, QuerySerializerMixin):
    language = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField('get_progress')
    is_enrolled = serializers.SerializerMethodField('get_enrollment')
    units_count = serializers.IntegerField(source='get_units_count')
    lectures_count = serializers.IntegerField(source='get_lectures_count')
    course_duration = serializers.CharField(source='get_lectures_duration')

    # Flag: this field hits the DB
    is_finished = serializers.SerializerMethodField('get_activity_status')

    privacy = CoursePrivacySerializer(many=False, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    default_plan = serializers.SerializerMethodField()

    PREFETCH_FIELDS = ['categories__course_set', 'privacy__shared_with']


    class Meta:
        model = Course
        fields = (
        'id', 'image', 'title',
        'description', 'objectives', 'about',
        'categories', 'tags', 'language',
        'privacy', 
        'default_plan',
        'units_count', 
        'lectures_count', 
        'course_duration', 
        'progress', 
        'is_enrolled', 
        'is_finished', 
        'is_free', 
        'date_created'
        )

    def get_progress(self, course):
         user = self.context.get('request', None).user
         content_viewed_count = course.activity.filter(user=user).count()

         content_count = course.get_lectures_count()
         if not content_count:
             return 0.0
         return content_viewed_count/content_count*100

    def get_enrollment(self, course):
         user = self.context.get('request', None).user
         return course.is_enrolled(user=user)

    def get_activity_status(self, course):
        user = self.context.get('request', None).user
        return course.is_finished(user)

    def format_lectures_duration(self, course):
        return seconds_to_duration(course.course_duration)

    def get_language(self, course):
        return course.get_language_display()

    def get_default_plan(self, course):
        request = self.context.get('request', None)
        pricing_plan = course.get_default_pricing_plan(request)
        return CoursePricingPlanSerializer(pricing_plan, many=False).data


class ReplySerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    class Meta:
        model = Reply
        fields = ("id", "body", "teacher", "created_at")

    def get_teacher(self, reply):
        return BasicUserSerializer(reply.created_by, many=False).data

class DiscussionSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    replies = ReplySerializer(many=True, read_only=True)
    class Meta:
        model = Discussion
        fields = ("id", "body", "student", "created_at", "replies")

    def get_student(self, discussion):
        return BasicUserSerializer(discussion.user, many=False).data
