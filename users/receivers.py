from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, Student, Teacher, LoggedInUser
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import user_logged_in, user_logged_out

UserModel = settings.AUTH_USER_MODEL

@receiver(pre_save, sender=UserModel)
def pre_save_user(sender, instance=None, created=False, **kwargs):

    if instance.id:
        old_instance = User.objects.get(id=instance.id)
        if old_instance.is_teacher != instance.is_teacher and not instance.is_teacher:
            instance.delete_teacher_profile()
        if old_instance.is_student != instance.is_student and not instance.is_student:
            instance.delete_student_profile()

    if instance.is_student and not hasattr(instance, 'student_profile'):
        instance.create_student_profile()
    if instance.is_teacher and not hasattr(instance, 'teacher_profile'):
        instance.create_teacher_profile()


@receiver(post_save, sender=UserModel)
def post_save_user(sender, instance=None, created=False, **kwargs):
    if instance.is_reached_screenshots_limit:
        instance.block()

@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    LoggedInUser.objects.get_or_create(user=kwargs.get('user'))


@receiver(user_logged_out)
def on_user_logged_out(sender, **kwargs):
    LoggedInUser.objects.filter(user=kwargs.get('user')).delete()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('users_api:reset-password')),
            reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('users/reset_password_email_form.html', context)
    email_plaintext_message = render_to_string('users/reset_password_email_form.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Emtyaz Advisor"),
        # message:
        email_plaintext_message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
#
# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
#
#     title = "Reset your {title} account password".format(title="Emtyaz Advisor")
#     email_plaintext_message = f"""
#     Dear {reset_password_token.user.username},
#
#     This is a secret key to reset your password: {reset_password_token.key}
#
#     If you did not make the request, please ignore this message and your password will remain unchanged.
#     """
#     send_mail(
#         # title:
#         "Password Reset for {title}".format(title="Emtyaz Advisor"),
#         # message:
#         email_plaintext_message,
#         # from:
#         settings.EMAIL_HOST_USER,
#         # to:
#         [reset_password_token.user.email]
#     )
