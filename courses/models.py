from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q, Sum, Count
from django.db.models.functions import Cast
from django.conf import settings
from model_utils import Choices
from categories.models import Category, ReferenceCategory, Tag
import datetime
from alteby.utils import seconds_to_duration
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from pathlib import Path
import cv2
from moviepy.editor import VideoFileClip
from .utils import get_lecture_path
from .managers import CustomCourseManager
from main.models import UserActionModel, TimeStampedModel

from users.models import User, Teacher
UserModel = settings.AUTH_USER_MODEL

####### Quizzes section
class Quiz(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'quizzes'

    def __str__(self):
          return self.name

    def get_questions_count(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_title = models.TextField()
    question_extra_info = models.TextField(blank=True, null=True)

    def __str__(self):
          return self.question_title


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
          return f'{self.question}-{self.choice}'


class QuizResult(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="quiz_result")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="result")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}-{self.quiz}'

    def save(self, *args, **kwargs):
        if self.selected_choice.is_correct:
            self.is_correct = True
        else:
            self.is_correct = False
        super(QuizResult, self).save(*args, **kwargs) # Call the "real" save() method.


class QuizAttempt(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_attempts")

    def __str__(self):
        return f'{self.user}-{self.quiz}'


####### Course Section
class Course(UserActionModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField(Category, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to="courses/images", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = CustomCourseManager()

    def __str__(self):
          return self.title

    def atomic_post_save(self, sender, created, **kwargs):
        CoursePrivacy.objects.get_or_create(course=self)

    def can_access(self, user):
        if self.privacy.is_public():
            return True
        elif self.privacy.is_private():
            return False
        else:
            return user in self.privacy.shared_with.all()

    def delete_course_activity(self):
        CourseActivity.objects.filter(course=self).delete()
        return True

    def get_units_count(self):
        return self.units.count()

    def get_lectures_count(self):
        return self.units.aggregate(count=Count('topics__lectures'))['count']

    def get_lectures_duration(self):
        duration = self.units.aggregate(sum=Sum('topics__lectures__duration'))['sum']
        if not duration:
            duration = 0
        return duration

    def is_finished(self, user):
        lectures = Lecture.objects.filter(topic__unit__course=self)
        if not lectures:
            return False
        activity = self.activity.filter(user=user, lecture__in=lectures).count()
        return len(lectures) == activity

    def get_contributed_teachers(self):
        course_units_ids = self.units.values_list('id', flat=True)
        course_topics_ids = Topic.objects.filter(unit__in=course_units_ids).values_list('id', flat=True)
        teachers_ids_list = Lecture.objects.filter(topic__in=course_topics_ids).values_list("teacher", flat=True)
        teachers_list = User.objects.filter(id__in=teachers_ids_list)
        return teachers_list

    @property
    def comments(self):
        return Comment.objects.filter(object_type=ContentType.objects.get_for_model(self).id, status='published')


class Unit(UserActionModel, TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    title = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_topics_count(self):
        return self.topics.count()

    def get_lectures_count(self):
        return self.topics.aggregate(count=Count('lectures'))['count']

    def get_lectures_duration(self):
        duration = self.topics.aggregate(sum=Sum('lectures__duration'))['sum']

        if not duration:
            duration = 0
        return duration

    def is_finished(self, user):
        topics_ids = self.topics.all().values_list('id', flat=True)
        lectures = Lecture.objects.filter(topic__in=topics_ids)
        activity = self.course.activity.filter(user=user, lecture__in=lectures).count()
        return len(lectures) == activity

class Topic(UserActionModel, TimeStampedModel):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='topics')
    title = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_lectures_count(self):
        return self.lectures.count()

    def get_lectures_duration(self):
        duration = self.lectures.aggregate(sum=Sum('duration'))['sum']
        if not duration:
            duration = 0
        return duration

    def is_finished(self, user):
        lectures = self.lectures.all()
        activity = self.unit.course.activity.filter(user=user, lecture__in=lectures).count()
        return len(lectures) == activity

######### Topic Lecture section
class Lecture(UserActionModel, TimeStampedModel):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="lectures")
    title = models.CharField(max_length=100)
    description = models.TextField()
    video = models.FileField(upload_to=get_lecture_path, blank=True, null=True)
    audio = models.FileField(upload_to='audio', blank=True, null=True)
    text = models.TextField(blank=True, null=True, max_length=100)
    duration = models.FloatField(blank=True, default=0)
    order = models.IntegerField()
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, blank=True, null=True, on_delete=models.CASCADE, related_name="contributed_lectures")
    references = models.ManyToManyField("courses.Reference", blank=True)

    class Meta:
        ordering = ('-date_created', )

    def __str__(self):
          return self.title

    # def save(self, *args, **kwargs):
    #     old_lecture = type(self).objects.get(pk=self.pk) if self.pk else None
    #     super(Lecture, self).save(*args, **kwargs)
    #     if old_lecture and old.video != self.video: # Field has changed
    #         do_something(self)

    def atomic_post_save(self, sender, created, **kwargs):
        LecturePrivacy.objects.get_or_create(lecture=self)

    def can_access(self, user):
        if self.privacy.is_public():
            return True
        elif self.privacy.is_private():
            return False
        else:
            return user in self.privacy.shared_with.all()

    @property
    def comments(self):
        return Comment.objects.filter(object_type=ContentType.objects.get_for_model(self).id, status='published')

    def delete_qualities(self):
        LectureQuality.objects.filter(lecture=self).delete()
        return True

    def extract_and_set_audio(self):

        if not self.video:
            self.reset_audio()
            return False

        video = VideoFileClip(self.video.path)
        audio = video.audio
        if not audio:
            self.reset_audio()
            return False

        video_path = Path(self.video.path)
        audio_path = video_path.with_suffix('.mp3')
        out_audio = audio.write_audiofile(audio_path)

        self.audio = str(Path(self.video.name).with_suffix('.mp3'))
        self.save()
        return True

    def detect_and_change_video_duration(self):

        if self.video:
            self.duration = VideoFileClip(self.video.path).duration
        else:
            self.duration = 0
        self.save()
        return self.duration

    def detect_original_video_quality(self):

        video = cv2.VideoCapture(self.video.path)
        quality = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        quality = self.__class__.scale_quality(quality)
        quality_attribute = getattr(LectureQuality.Qualities, f"_{quality}")
        if not quality_attribute:
            return None

        original_quality, created = LectureQuality.objects.get_or_create(
        lecture=self,
        video=str(self.video.name),
        quality=quality_attribute
        )
        return original_quality

    def reset_audio(self):
        self.audio = None
        self.save()

    def reset_duration(self):
        self.duration = 0
        self.save()

    @classmethod
    def convert_video_quality(cls, video_path, quality):
        from .utils import get_resolution

        found, width, height = get_resolution(quality)
        if not found:
            return None, False

        video = VideoFileClip(video_path)
        clip_resized = video.resize(height=height)

        video_name = Path(video_path)
        new_video_name = f'{video_name.stem}_{quality}{video_name.suffix}'
        new_video_path = Path(video_path).parent.joinpath(new_video_name)

        clip_resized.write_videofile(
        str(new_video_path),
        temp_audiofile=Path(video_path).parent.joinpath('temp-audio.m4a'),
        remove_temp=True,
        codec="libx264",
        audio_codec="aac"
        )
        return new_video_name, True

    @classmethod
    def get_supported_qualities(cls, quality):
        qualities = [144, 240, 360, 480, 720, 1080]
        if quality not in qualities:
            if quality > 720 or quality > 1080:
                quality = 1080
            elif quality > 480:
                quality = 720
            elif quality > 360:
                quality = 480
            elif quality > 240:
                quality = 360
            elif quality > 144:
                quality = 240
            else:
                return []

        quality_index = qualities.index(quality)
        supported_qualities = qualities[:quality_index]
        return supported_qualities

    @classmethod
    def scale_quality(cls, quality):
        if quality > 1080:
            return 1080
        elif quality > 720:
            return 1080
        elif quality > 480:
            return 720
        elif quality > 360:
            return 480
        elif quality > 240:
            return 360
        elif quality > 144:
            return 240
        else:
            return 144

###### Course Activity Tracking
class CourseActivity(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='course_activity')
    is_finished = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='activity')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='activity')
    left_off_at = models.FloatField(default=0, validators=[
            MinValueValidator(0)
    ])

    class Meta:
        verbose_name_plural = 'Courses Activity Tracker'

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.lecture.title}'


#### Comments and feedback section
class PublishedCommentsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Comment(models.Model):

    STATUS_CHOICES = Choices(
        ('pending', 'Pending'),
        ('published', 'Published'),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="comments")

    choices = Q(app_label = 'courses', model = 'course') | Q(app_label = 'courses', model = 'lecture')

    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=choices, related_name='comments')
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('object_type', 'object_id')

    comment_body = models.TextField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES.pending)
    date_created = models.DateTimeField(auto_now_add=True)

    # Default manager
    objects = models.Manager()


    def __str__(self):
        return f'{self.user.email}-{self.comment_body}'


class Feedback(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="feedbacks")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.IntegerField(
    validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_rating",
                check=models.Q(rating__range=(1, 5)),
            ),
        ]

    def __str__(self):
          return f'{self.user.email}-{self.course.title}'


### User's Requests section
class CorrectInfo(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    min_from = models.CharField(blank=True, max_length=100)
    min_to = models.CharField(blank=True, max_length=100)
    scientific_evidence = models.TextField(blank=True)

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.lecture.title}'


class Report(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.lecture.title}'


## Privacy section
class Privacy(UserActionModel, TimeStampedModel):

    PRIVACY_CHOICES = Choices(
        ('public', 'Public'),
        ('private', 'Private'),
        ('custom', 'Custom'),
    )

    option = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default=PRIVACY_CHOICES.private)
    shared_with = models.ManyToManyField(UserModel, blank=True)

    def is_public(self):
        return self.option == self.PRIVACY_CHOICES.public

    def is_private(self):
        return self.option == self.PRIVACY_CHOICES.private

    def is_custom(self):
        return self.option == self.PRIVACY_CHOICES.custom



class CoursePrivacy(Privacy):

    course = models.OneToOneField(Course, on_delete=models.CASCADE, blank=True, related_name="privacy")

    def __str__(self):
          return self.course.title


class LecturePrivacy(Privacy):

    lecture = models.OneToOneField(Lecture, on_delete=models.CASCADE, blank=True, related_name="privacy")

    def __str__(self):
          return self.lecture.title

# Attachments section
class Attachement(UserActionModel, TimeStampedModel):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='attachements')


class CourseAttachement(Attachement):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attachments")
    def __str__(self):
          return self.course.title

class LectureAttachement(Attachement):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="attachments")
    def __str__(self):
          return self.lecture.title

class LectureQuality(models.Model):

    class Qualities(models.IntegerChoices):
        _2160 = 2160, ("2160p")
        _1440 = 1440, ("1440p")
        _1080 = 1080, ("1080p")
        _720 = 720, ("720p")
        _480 = 480, ("480p")
        _360 = 360, ("360p")
        _240 = 240, ("240p")
        _144 = 144, ("144p")

    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="qualities")
    video = models.FileField()
    quality = models.CharField(choices=Qualities.choices, max_length=20)

    class Meta:
        verbose_name_plural = 'Lecture Qualities'
        ordering = ('-quality',)

    def __str__(self):
        return f'{self.lecture}-{self.quality}'

    def get_quality_display(self):
        quality = getattr(self.Qualities, f'_{self.quality}')
        return quality.label

class Reference(UserActionModel, TimeStampedModel):

    class ReferenceType(models.TextChoices):
        website = "website", ("Website")
        book = "book", ("Book")
        link = "link", ("Link")
        paper = "paper", ("Paper")
        journal = "journal", ("Journal")

    name = models.CharField(max_length=100)
    type = models.CharField(choices=ReferenceType.choices, max_length=20)
    link = models.URLField(blank=True)
    categories = models.ManyToManyField(ReferenceCategory, blank=True)

    def __str__(self):
        return self.name
