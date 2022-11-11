from django.db import models
from main.utility_models import UserActionModel, TimeStampedModel
from courses.models.activity import CourseActivity
from courses.models.lecture import Lecture
from alteby.utils import render_alert
from django.core.exceptions import ValidationError

class Topic(UserActionModel, TimeStampedModel):
    unit = models.ForeignKey("courses.Unit", on_delete=models.CASCADE, related_name='topics')
    title = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['unit']),
        ]

    def __str__(self):
        return f"ID: {self.id} - {self.title}"

    def get_lectures(self):
        lectures_queryset = Lecture.objects.filter(assigned_topics__topic__id=self.id)
        return lectures_queryset
    
    def get_lectures_count(self):
        return self.assigned_lectures.count()

    def get_lectures_duration(self):
        duration = self.assigned_lectures.aggregate(sum=models.Sum('lecture__duration'))['sum']
        if not duration:
            duration = 0
        return duration

    def get_lectures_viewed_count(self, user):
        lectures_queryset = self.get_lectures()
        lectures_viewed = CourseActivity.objects.filter(lecture__in=lectures_queryset, user=user).count()
        return lectures_viewed

    def is_finished(self, user):
        lectures_viewed_count = self.get_lectures_viewed_count(user=user)
        return self.get_lectures_count() == lectures_viewed_count
