from django.db import models 
from main.utility_models import TimeStampedModel
from question_banks.utils import get_choice_path


class Choice(TimeStampedModel):
    question = models.ForeignKey("question_banks.Question", on_delete=models.CASCADE, related_name="choices")
    choice = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    explanation = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_choice_path, blank=True)

    def __str__(self):
          return f'{self.question}-{self.choice}'
