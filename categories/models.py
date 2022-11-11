from django.db import models
from main.utility_models import UserActionModel, TimeStampedModel

class Category(UserActionModel, TimeStampedModel):

    name = models.CharField(max_length=40, unique=True)
    icon = models.FileField(upload_to='categories/icons')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class ReferenceCategory(UserActionModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    icon = models.FileField(blank=True, null=True, upload_to='references_categories/icons')

    class Meta:
        verbose_name_plural = 'References Categories'

    def __str__(self):
        return self.name

class Tag(UserActionModel, TimeStampedModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
