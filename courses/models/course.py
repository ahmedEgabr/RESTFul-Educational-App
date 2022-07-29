from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.contenttypes.models import ContentType
from main.models import UserActionModel, TimeStampedModel
from courses.managers import CustomCourseManager
from courses.models.discussion import Discussion
from courses.models.lecture import Lecture
from courses.models.topic import Topic
from courses.models.course_privacy import CoursePrivacy
from courses.models.activity import CourseActivity
from courses.models.reference import Reference
from users.models import User, Teacher


class Course(UserActionModel):

    class Languages(models.TextChoices):
        arabic = "arabic", ("Arabic")
        english = "english", ("English")
        mixed = "mixed", ("Mixed")

    title = models.CharField(max_length=100)
    description = RichTextField()
    objectives = RichTextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField("categories.Category", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    quiz = models.OneToOneField("courses.Quiz", on_delete=models.CASCADE, blank=True, null=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to="courses/images", blank=True)
    tags = models.ManyToManyField("categories.Tag", blank=True)
    language = models.CharField(choices=Languages.choices, default=Languages.arabic, max_length=20)

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
