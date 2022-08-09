from django.db import models 
from main.utility_models import TimeStampedModel


class QuestionResult(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="questions_result")
    quiz = models.ForeignKey("courses.Quiz", on_delete=models.PROTECT, related_name="result")
    question = models.ForeignKey("question_banks.Question", on_delete=models.PROTECT)
    selected_choice = models.ForeignKey("question_banks.Choice", on_delete=models.PROTECT)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}-{self.quiz}'

    def save(self, *args, **kwargs):
        if self.selected_choice.is_correct:
            self.is_correct = True
        else:
            self.is_correct = False
        super(QuestionResult, self).save(*args, **kwargs) # Call the "real" save() method.
