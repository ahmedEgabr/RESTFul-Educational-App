from django.db import models 
from ckeditor.fields import RichTextField
from main.utility_models import TimeStampedModel, UserActionModel
from question_banks.utils import get_question_path


class Question(TimeStampedModel, UserActionModel):
    title = RichTextField()
    image = models.ImageField(upload_to=get_question_path, blank=True)
    extra_info = RichTextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference}"
    
    @property
    def reference(self):
        reference = None
        if self.id:
            COUNT_OFFSET = 1000
            reference = self.id + COUNT_OFFSET
        return reference
