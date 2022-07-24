from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from courses.models import (
Course, Unit, Topic,
CourseActivity,
Lecture, LectureQuality, CoursePrivacy,
LecturePrivacy,
Quiz, QuizResult, Question, Choice,
Attachement, Comment, Feedback,
LectureExternalLink, Reference
)
from alteby.utils import seconds_to_duration
from categories.api.serializers import CategorySerializer, TagSerializer
from django.db.models import Sum
from payment.models import CourseEnrollment
from courses.utils import allowed_to_access_lecture
from users.api.serializers import TeacherSerializer


class LectureIndexSerialiser(serializers.ModelSerializer):

    can_access = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = ('id', 'title', 'can_access')

    def get_can_access(self, lecture):
        user = self.context.get('user', None)
        return lecture.can_access(user) or lecture.is_enrolled


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
        fields = ('id', 'choice', 'is_correct')

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ('id', 'question_title', 'choices')

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    # number_of_questions = serializers.CharField(source='get_questions_count')
    class Meta:
        model = Quiz
        fields = ('id', 'name', 'description', 'questions')

class BaseQuizResultSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False, read_only=True)
    selected_choice = ChoiceSerializer(many=False, read_only=True)
    class Meta:
        model = QuizResult
        fields = ('id', 'question', 'selected_choice', 'is_correct')

class QuizResultSerializer(serializers.ModelSerializer):
    selected_choice = ChoiceSerializer(many=False, read_only=True)
    result = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField('get_questions_count')
    score = serializers.SerializerMethodField('get_score')
    class Meta:
        model = Quiz
        fields = '__all__'

    num_of_right_answers = 0
    def get_result(self, quiz):
        user = self.context.get('request', None).user
        # Must select distinct, but it is not supported by SQLite
        quiz_answers = QuizResult.objects.select_related('question', 'selected_choice').prefetch_related('question__choices').filter(user=user, quiz=quiz)
        self.num_of_right_answers = quiz_answers.filter(is_correct=True).count()
        return BaseQuizResultSerializer(quiz_answers, many=True, read_only=True).data

    def get_score(self, quiz):
        return self.num_of_right_answers


    def get_questions_count(self, quiz):
        return quiz.questions.count()

class CoursePrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePrivacy
        exclude = ("created_at", "updated_at", "created_by", "updated_by")

class LecturePrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturePrivacy
        exclude = ("created_at", "updated_at")

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

    class Meta:
        model = Lecture
        fields = (
        'id',
        'title',
        'description',
        'objectives',
        'order',
        'topic',
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
        'privacy'
        )

    def convert_duration(self, lecture):
        return seconds_to_duration(lecture.duration)

    def get_course_id(self, lecture):
        return lecture.course.id

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

    class Meta:
        model = Topic
        fields =('id', 'title', 'unit', 'lectures_count', 'lectures_duration', 'is_finished', 'order')

    def get_activity_status(self, topic):
        if not topic.lectures_count:
            return False
        return topic.lectures_count == topic.num_of_lectures_viewed

    def format_lectures_duration(self, topic):
        return seconds_to_duration(topic.lectures_duration)


class TopicDetailSerializer(serializers.ModelSerializer):
    lectures_count = serializers.IntegerField()
    lectures_duration = serializers.FloatField()
    is_finished = serializers.SerializerMethodField('get_activity_status')

    class Meta:
        model = Topic
        fields =('id', 'title', 'unit', 'lectures_count', 'lectures_duration', 'is_finished', 'order')

    def get_activity_status(self, topic):
        if not topic.lectures_count:
            return False
        return topic.lectures_count == topic.num_of_lectures_viewed

    def format_lectures_duration(self, topic):
        return seconds_to_duration(topic.lectures_duration)

class UnitSerializer(serializers.ModelSerializer):
    lectures_count = serializers.IntegerField()
    lectures_duration = serializers.FloatField()
    is_finished = serializers.SerializerMethodField('get_activity_status')

    class Meta:
        model = Unit
        fields = ('id', 'title', 'course', 'order', 'lectures_duration', 'lectures_count', 'is_finished')

    def get_activity_status(self, unit):
        if not unit.lectures_count:
            return False
        return unit.lectures_count == unit.num_of_lectures_viewed

    def format_lectures_duration(self, unit):
        return seconds_to_duration(unit.lectures_duration)

class UnitTopicsSerializer(serializers.ModelSerializer):
    topics = TopicsListSerializer(many=True, read_only=True)
    lectures_count = serializers.IntegerField(source='get_lectures_count')
    lectures_duration = serializers.CharField(source='get_lectures_duration')
    class Meta:
        model = Unit
        fields = ('id', 'title', 'course', 'order', 'topics', 'lectures_duration', 'lectures_count')

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

    PREFETCH_FIELDS = ['categories__course_set', 'privacy__shared_with']


    class Meta:
        model = Course
        fields = (
        'id', 'image', 'title',
        'description', 'objectives', 'about',
        'categories', 'tags', 'price', 'language',
        'privacy', 'quiz',
        'units_count', 'lectures_count', 'course_duration', 'progress', 'is_enrolled', 'is_finished', 'date_created')

    def get_progress(self, course):
         user = self.context.get('request', None).user
         content_viewed_count = course.activity.filter(user=user).count()

         content_count = course.get_lectures_count()
         if not content_count:
             return 0.0
         return content_viewed_count/content_count*100

    def get_enrollment(self, course):
         user = self.context.get('request', None).user
         return CourseEnrollment.objects.filter(user=user, course=course).exists()

    def get_activity_status(self, course):
        user = self.context.get('request', None).user
        return course.is_finished(user)

    def format_lectures_duration(self, course):
        return seconds_to_duration(course.course_duration)

    def get_language(self, course):
        return course.get_language_display()


class CoursesSerializer(serializers.ModelSerializer, QuerySerializerMixin):
    langauge = serializers.SerializerMethodField()
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

    PREFETCH_FIELDS = ['categories__course_set', 'privacy__shared_with']


    class Meta:
        model = Course
        fields = (
        'id', 'image', 'title',
        'description', 'objectives', 'about',
        'categories', 'tags', 'price', 'language',
        'privacy', 'quiz',
        'units_count', 'lectures_count', 'course_duration', 'progress', 'is_enrolled', 'is_finished', 'date_created')

    def get_progress(self, course):
         user = self.context.get('request', None).user
         content_viewed_count = course.activity.filter(user=user).count()

         content_count = course.get_lectures_count()
         if not content_count:
             return 0.0
         return content_viewed_count/content_count*100

    def get_enrollment(self, course):
         user = self.context.get('request', None).user
         return CourseEnrollment.objects.filter(user=user, course=course).exists()

    def get_activity_status(self, course):
        user = self.context.get('request', None).user
        return course.is_finished(user)

    def format_lectures_duration(self, course):
        return seconds_to_duration(course.course_duration)

    def get_language(self, course):
        return course.get_language_display()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
