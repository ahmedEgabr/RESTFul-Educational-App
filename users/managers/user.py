from django.db import models, transaction
from django.contrib.auth.models import BaseUserManager



class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, is_staff=False, is_superuser=False, is_teacher=False, is_student=True):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise VlaueError('User must have a username')

        user = self.model(
                        email=self.normalize_email(email),
                        username=username,
                        is_staff=is_staff,
                        is_superuser=is_superuser,
                        is_teacher=is_teacher,
                        is_student=is_student
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    @transaction.atomic
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            is_staff = True,
            is_superuser = True,
            is_teacher = False,
            is_student = False
        )
        user.save(using = self._db)
        return user
