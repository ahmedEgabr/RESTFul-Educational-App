from django.db import models
from django.core.validators import MinValueValidator
from main.models import TimeStampedModel

class CourseActivity(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='course_activity')
    is_finished = models.BooleanField(default=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name='activity')
    lecture = models.ForeignKey("courses.Lecture", on_delete=models.CASCADE, related_name='activity')
    left_off_at = models.FloatField(default=0, validators=[
            MinValueValidator(0)
    ])

    class Meta:
        verbose_name_plural = 'Courses Activity Tracker'

    def __str__(self):
          return f'{self.user.email}-{self.course.title}-{self.lecture.title}'
