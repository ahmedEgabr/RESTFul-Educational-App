from django.db import models
from django_currentuser.db.models import CurrentUserField


class UserActionModel(models.Model):
    """
    Provides created_by updated_by fields if you have an instance of user,
    you can get all the items, with Item being the model name, created or updated
    by user using user.created_(classname)s() or user.updated_(classname)s()
    """
    created_by = CurrentUserField(related_name='created_%(class)ss')
    updated_by = CurrentUserField(on_update=True, related_name='updated_%(class)ss')

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    Provides created_at updated_at fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContactUs(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=100)
    telegram_username = models.CharField(max_length=100)
    messenger_username = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Contact Us'

    def __str__(self):
        return self.email
