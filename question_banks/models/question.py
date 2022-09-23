from django.db import models 
from django.conf import settings
from ckeditor.fields import RichTextField
from main.utility_models import TimeStampedModel, UserActionModel
from question_banks.utils import get_question_path


class Question(TimeStampedModel, UserActionModel):
    reference = models.IntegerField(null=True, blank=True)
    title = RichTextField()
    image = models.ImageField(upload_to=get_question_path, blank=True)
    extra_info = RichTextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference}"
    
    def get_reference(self):
        reference = None
        if self.id:
            reference = self.id + settings.COUNT_OFFSET
        return reference
