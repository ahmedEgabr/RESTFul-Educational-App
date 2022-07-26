from django.db import models
from django.core.exceptions import ValidationError
from .time_stamp import TimeStampedModel

class ContactUs(TimeStampedModel):
    email = models.EmailField()
    phone_number = models.CharField(max_length=100)
    telegram_username = models.CharField(max_length=100)
    messenger_username = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Contact Us'

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.pk and self.__class__.objects.exists():
        # if you'll not check for self.pk
        # then error will also raised in update of exists model
            raise ValidationError('There is can be only one Contact Us.')
        return super(ContactUs, self).save(*args, **kwargs)
