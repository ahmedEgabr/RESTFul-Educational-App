from django.db import models
from main.utility_models import TimeStampedModel


class CoursesGroup(TimeStampedModel):
    name = models.CharField(max_length=50)
    courses = models.ManyToManyField("courses.Course")
    
    def __str__(self) -> str:
        return self.name
