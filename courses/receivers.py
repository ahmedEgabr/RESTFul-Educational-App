import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.db import transaction
from .models import QuizAttempt, Lecture, LectureQuality, Course, CoursePricingPlan, CoursePlanPrice
from moviepy.editor import VideoFileClip, AudioFileClip

def atomic_post_save(sender, instance, **kwargs):
    if hasattr(instance, "atomic_post_save") and transaction.get_connection().in_atomic_block:
        transaction.on_commit(lambda: instance.atomic_post_save(sender, instance=instance, **kwargs))

post_save.connect(atomic_post_save)


@receiver(pre_save, sender=CoursePricingPlan)
def pre_save_course_pricing_plan(sender, instance, *args, **kwargs):
    
    if instance.lifetime_access:
        instance.durantion = None
        instance.duration_type = None
        
    # set the first plan as a default
    course_has_plans = sender.objects.filter(
    course=instance.course, is_active=True
    ).exists()
    if not course_has_plans:
        instance.is_default = True

        # Update course pricing
        instance.course.is_free = False
        instance.course.save()

# @receiver(post_save, sender=CoursePricingPlan)
# def post_save_course_pricing_plan(sender, instance=None, created=False, **kwargs):
#     prices = instance.prices.filter(is_active=True)
#     if prices.count() == 1:
#         price = prices.first()
#         price.is_default = True
#         price.save()
        
        
@receiver(pre_save, sender=CoursePlanPrice)
def pre_save_course_plan_prices(sender, instance, *args, **kwargs):
    if instance.select_all_countries:
        instance.countries = []
    if instance.is_free_for_selected_countries:
        instance.amount = 0
        instance.currency = None
    
@receiver(post_save, sender=CoursePricingPlan)
def deactivate_plan_prices(sender, instance=None, created=False, **kwargs):
    if instance.is_free_for_all_countries:
        instance.prices.update(is_active=False)
        
@receiver(post_delete, sender=CoursePricingPlan)
def post_delete_course_pricing_plan(sender, instance, **kwargs):

    course_has_plans = sender.objects.filter(
    course=instance.course, is_active=True
    ).exists()
    if not course_has_plans:
        # Update course pricing
        instance.course.is_free = True
        instance.course.save()

@receiver(post_save, sender=CoursePlanPrice)
def deactivate_plan_prices(sender, instance=None, created=False, **kwargs):
    if instance.select_all_countries:
        instance.plan.prices.exclude(id=instance.id).update(is_active=False)

@receiver(post_delete, sender=CoursePlanPrice)
def post_delete_plan_price(sender, instance, **kwargs):
   if instance.plan.prices.filter(is_active=True).count() == 1:
       price = instance.plan.prices.first()
       price.is_default = True
       price.save()
        

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
