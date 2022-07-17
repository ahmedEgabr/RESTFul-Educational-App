from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from model_utils import Choices
from main.models import TimeStampedModel

class PublishedCommentsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Comment(TimeStampedModel):

    STATUS_CHOICES = Choices(
        ('pending', 'Pending'),
        ('published', 'Published'),
    )

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comments")

    choices = models.Q(app_label = 'courses', model = 'course') | models.Q(app_label = 'courses', model = 'lecture')

    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=choices, related_name='comments')
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('object_type', 'object_id')

    comment_body = models.TextField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES.pending)

    # Default manager
    objects = models.Manager()


    def __str__(self):
        return f'{self.user.email}-{self.comment_body}'
