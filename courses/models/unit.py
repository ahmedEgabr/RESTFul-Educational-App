from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from main.utility_models import UserActionModel, TimeStampedModel
from courses.models import Lecture
from alteby.utils import render_alert


class Unit(UserActionModel, TimeStampedModel):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name='units')
    title = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['course']),
        ]

    def __str__(self):
        return self.title
    
    def clean_fields(self, **kwargs):
        # if self.__class__.objects.filter(course=self.course, order=self.order).exclude(id=self.id).exists():
        #     raise ValidationError(
        #         {
        #             "order": render_alert(
        #                 """
        #                 Unit with the same order is already exists.
        #                 """,
        #                 tag="strong",
        #                 error=True  
        #                 )
        #         }
        #     ) 
        super(Unit, self).clean_fields(**kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Unit, self).save(*args, **kwargs)

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
