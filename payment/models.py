from django.db import models
from courses.models import Course
from model_utils import Choices
from django.conf import settings
from main.models import UserActionModel, TimeStampedModel
UserModel = settings.AUTH_USER_MODEL

class CourseEnrollment(UserActionModel):

    PAYMENT_METHODS = Choices(
        ('online', 'Online'),
        ('offline', 'Offline'),
    )

    PAYMENT_TYPES = Choices(
        ('telegram', 'Telegram'),
        ('fawry', 'Fawry'),
        ('visa', 'Visa'),
        ('free', 'Free'),
    )
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default=PAYMENT_METHODS.online)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default=PAYMENT_TYPES.free)
    date_created = models.DateTimeField(auto_now_add=True)
