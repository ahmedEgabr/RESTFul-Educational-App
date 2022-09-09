from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(
    "users.User",
    on_delete=models.CASCADE,
    primary_key=True,
    related_name="teacher_profile"
    )
    major = models.CharField(blank=True, max_length=40)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

    def activate(self):
        if not self.is_active:
            self.is_active = False
            self.save()

    def deactivate(self):
        self.is_active = False
        self.save()
