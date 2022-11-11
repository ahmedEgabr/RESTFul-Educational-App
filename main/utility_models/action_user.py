from django.db import models
from django_currentuser.db.models import CurrentUserField


class UserActionModel(models.Model):
    """
    Provides created_by updated_by fields if you have an instance of user,
    you can get all the items, with Item being the model name, created or updated
    by user using user.created_(classname)s() or user.updated_(classname)s()
    """
    created_by = CurrentUserField(blank=True, related_name='created_%(class)ss')
    updated_by = CurrentUserField(blank=True, on_update=True, related_name='updated_%(class)ss')

    class Meta:
        abstract = True
