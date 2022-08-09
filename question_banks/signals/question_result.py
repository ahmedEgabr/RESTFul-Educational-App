from django.db.models.signals import post_save
from question_banks.models import QuestionResult

# @receiver(post_save, sender=QuestionResult)
# def add_quiz_attempt(sender, instance=None, created=False, **kwargs):
#     if created:
#         if instance.question == instance.quiz.questions.last():
#             QuizAttempt.objects.create(user=instance.user, quiz=instance.quiz)