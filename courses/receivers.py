import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.db import transaction
from .models import QuizAttempt, QuizResult, Lecture, LectureQuality
from moviepy.editor import VideoFileClip, AudioFileClip

def atomic_post_save(sender, instance, **kwargs):
    if hasattr(instance, "atomic_post_save") and transaction.get_connection().in_atomic_block:
        transaction.on_commit(lambda: instance.atomic_post_save(sender, instance=instance, **kwargs))

post_save.connect(atomic_post_save)


@receiver(post_save, sender=QuizResult)
def add_quiz_attempt(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.question == instance.quiz.questions.last():
            QuizAttempt.objects.create(user=instance.user, quiz=instance.quiz)

# @receiver(post_save, sender=Lecture)
# def calculate_duration(sender, instance=None, created=False, **kwargs):
#     if created:
#         if instance.video:
#             video = VideoFileClip(instance.video.path)
#             instance.duration = video.duration # this will return the length of the video in seconds
#             instance.save()
#     else:
#         if instance.video:
#             video = VideoFileClip(instance.video.path)
#             instance.duration = video.duration # this will return the length of the video in seconds
#             instance.save()

@receiver(post_delete, sender=LectureQuality)
def auto_delete_video_on_quality_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.video and os.path.isfile(instance.video.path):
        os.remove(instance.video.path)

@receiver(post_delete, sender=Lecture)
def auto_delete_video_and_audio_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.video and os.path.isfile(instance.video.path):
        os.remove(instance.video.path)

    if instance.audio and os.path.isfile(instance.audio.path):
        os.remove(instance.audio.path)

@receiver(pre_save, sender=Lecture)
def pre_save_lecture(sender, instance, *args, **kwargs):
    """ delete old video on video field change and reset audio """

    old_instance = instance.__class__.objects.filter(id=instance.id).first()
    if old_instance:
        try:
            old_video = old_instance.video.path
            try:
                new_video = instance.video.path
            except:
                new_video = None
            if new_video != old_video:
                if os.path.exists(old_video):
                    os.remove(old_video)

                if old_instance.audio:
                    old_audio = old_instance.audio.path
                    if os.path.exists(old_audio):
                        os.remove(old_audio)
                    instance.audio = None
        except:
            pass
