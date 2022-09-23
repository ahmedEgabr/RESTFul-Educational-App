from django.db.models.signals import post_save
from question_banks.models import Question
from django.dispatch import receiver


@receiver(post_save, sender=Question)
def question_post_save(sender, instance=None, created=False, **kwargs):
    if created:
        instance.reference = instance.get_reference()
        instance.save()