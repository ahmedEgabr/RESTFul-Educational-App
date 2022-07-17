from django.db import models

class Quiz(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'quizzes'

    def __str__(self):
          return self.name

    def get_questions_count(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_title = models.TextField()
    question_extra_info = models.TextField(blank=True, null=True)

    def __str__(self):
          return self.question_title


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
          return f'{self.question}-{self.choice}'


class QuizResult(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="quiz_result")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="result")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}-{self.quiz}'

    def save(self, *args, **kwargs):
        if self.selected_choice.is_correct:
            self.is_correct = True
        else:
            self.is_correct = False
        super(QuizResult, self).save(*args, **kwargs) # Call the "real" save() method.


class QuizAttempt(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_attempts")

    def __str__(self):
        return f'{self.user}-{self.quiz}'
