from django.db import models
from main.models import UserActionModel, TimeStampedModel


class Attachement(UserActionModel, TimeStampedModel):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='attachements')

    class Meta:
        abstract = True
