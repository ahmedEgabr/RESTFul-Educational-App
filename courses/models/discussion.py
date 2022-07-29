from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from model_utils import Choices
from main.models import TimeStampedModel
from courses.managers import DiscussionManager


class Discussion(TimeStampedModel):

    STATUS_CHOICES = Choices(
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    )

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="discussions")

    choices = models.Q(app_label = 'courses', model = 'course') | models.Q(app_label = 'courses', model = 'lecture')

    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=choices, related_name='discussions')
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('object_type', 'object_id')

    body = models.TextField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES.pending)

    # Default manager
    objects = DiscussionManager()

    class Meta:
        indexes = [
            models.Index(fields=["object_type", "object_id"]),
        ]

    def __str__(self):
        return f'{self.user.email}-{self.body}'
