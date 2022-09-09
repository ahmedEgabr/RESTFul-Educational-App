from django.db import models


# Model to store the list of logged in users
class LoggedInUser(models.Model):
    user = models.OneToOneField("users.User", related_name='logged_in_user', on_delete=models.CASCADE)
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.user.username
