from django.db import models
from main.models import UserActionModel, TimeStampedModel


class Reference(UserActionModel, TimeStampedModel):

    class ReferenceType(models.TextChoices):
        website = "website", ("Website")
        book = "book", ("Book")
        link = "link", ("Link")
        paper = "paper", ("Paper")
        journal = "journal", ("Journal")
        article = "article", ("Article")

    name = models.CharField(max_length=100)
    type = models.CharField(choices=ReferenceType.choices, max_length=20)
    link = models.URLField(blank=True)
    categories = models.ManyToManyField("categories.ReferenceCategory", blank=True)

    def __str__(self):
        return self.name
