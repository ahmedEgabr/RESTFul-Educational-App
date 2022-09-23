from django.db import models
from main.utility_models import TimeStampedModel


class PlanOffer(TimeStampedModel):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    plan = models.ForeignKey("courses.CoursePlan", on_delete=models.CASCADE)