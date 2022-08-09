from django.db import models
from main.utility_models import TimeStampedModel, UserActionModel


class Quiz(TimeStampedModel, UserActionModel):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    lecture = models.OneToOneField(
        "courses.Lecture", 
        on_delete=models.CASCADE, 
        blank=True,
        null=True,
        related_name="quiz"
        )
    questions = models.ManyToManyField("question_banks.Question")

    class Meta:
        verbose_name_plural = 'quizzes'

    def __str__(self):
          return self.name

    def get_questions_count(self):
        return self.questions.count()
        

class QuizAttempt(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    quiz = models.ForeignKey("courses.Quiz", on_delete=models.CASCADE, related_name="quiz_attempts")

    def __str__(self):
        return f'{self.user}-{self.quiz}'
