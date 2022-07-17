from django.db import models
from main.models import UserActionModel, TimeStampedModel

class Topic(UserActionModel, TimeStampedModel):
    unit = models.ForeignKey("courses.Unit", on_delete=models.CASCADE, related_name='topics')
    title = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_lectures_count(self):
        return self.lectures.count()

    def get_lectures_duration(self):
        duration = self.lectures.aggregate(sum=models.Sum('duration'))['sum']
        if not duration:
            duration = 0
        return duration

    def is_finished(self, user):
        lectures = self.lectures.all()
        activity = self.unit.course.activity.filter(user=user, lecture__in=lectures).count()
        return len(lectures) == activity
