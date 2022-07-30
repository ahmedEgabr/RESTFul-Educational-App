from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, BaseUserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.db.models import F, Q
from django.db import transaction
from django.contrib.auth.models import Group
from alteby.constants import TEACHER_GROUP, STUDENT_GROUP
from main.models import AppConfiguration
from users.managers import UserManager

# Account Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True, validators=[UnicodeUsernameValidator()])
    date_joined = models.DateTimeField(verbose_name="Date Joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="Last Login", auto_now=True)
    is_active = models.BooleanField('Active status', default=True)
    is_blocked = models.BooleanField('Is Blocked', default=False)
    is_staff = models.BooleanField('Staff status', default=False)
    is_teacher = models.BooleanField('Teacher status', default=False)
    is_student = models.BooleanField('Student status', default=False)
    screenshots_taken = models.IntegerField(
    blank=True, null=True, default=0, validators=[MinValueValidator(0)], verbose_name="Screenshots Taken"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, created=None, *args, **kwargs):
        super().save(*args, **kwargs)

    def block(self):
        if not self.is_blocked:
            self.is_blocked = True
            self.save()
        return True
        
    def activate(self):
        # Activate the User
        if not self.is_active:
            self.is_active = True
            self.save()

        # Deactivate User's Profile
        if self.is_teacher:
            teacher_profile = self.get_teacher_profile()
            if teacher_profile:
                teacher_profile.activate()
        if self.is_student:
            student_profile = self.get_student_profile()
            if student_profile:
                student_profile.activate()
        return True

    def deactivate(self):
        # Deactivate the User
        self.is_active = False
        self.save()

        # Deactivate User's Profile
        if self.is_teacher:
            teacher_profile = self.get_teacher_profile()
            if teacher_profile:
                teacher_profile.deactivate()
        if self.is_student:
            student_profile = self.get_student_profile()
            if student_profile:
                student_profile.deactivate()
        return True

    def record_a_screenshot(self):
        self.screenshots_taken += 1
        self.save()
        return self.screenshots_taken

    @property
    def is_reached_screenshots_limit(self):
        is_limit_reached = AppConfiguration.is_reached_screenshots_limit(self.screenshots_taken)
        if is_limit_reached:
            return True
        return False


    def create_student_profile(self):
        if self.is_student and not hasattr(self, "student_profile"):
            student_profile = Student.objects.create(user=self)
            student_group, created = Group.objects.get_or_create(name=STUDENT_GROUP)
            transaction.on_commit(lambda: self.groups.add(student_group))
            return student_profile
        return None

    def delete_student_profile(self):
        if hasattr(self, "student_profile"):
            self.student_profile.delete()
            student_group, created = Group.objects.get_or_create(name=STUDENT_GROUP)
            transaction.on_commit(lambda: self.groups.remove(student_group))
            return True
        return False

    def get_student_profile(self):
        if not self.is_student:
            return None
        if not hasattr(self, "student_profile"):
            return None
        if not self.student_profile.is_active:
            return None
        return self.student_profile

    def create_teacher_profile(self):
        if self.is_teacher and not hasattr(self, "teacher_profile"):
            teacher_profile = Teacher.objects.create(user=self)
            teacher_group, created = Group.objects.get_or_create(name=TEACHER_GROUP)
            transaction.on_commit(lambda: self.groups.add(teacher_group))
            return teacher_profile
        return None

    def delete_teacher_profile(self):
        if hasattr(self, "teacher_profile"):
            self.teacher_profile.delete()
            teacher_group, created = Group.objects.get_or_create(name=TEACHER_GROUP)
            transaction.on_commit(lambda: self.groups.remove(teacher_group))
            return True
        return False

    def get_teacher_profile(self):
        if not self.is_teacher:
            return None
        if not hasattr(self, "teacher_profile"):
            return None
        if not self.teacher_profile.is_active:
            return None
        return self.teacher_profile

    @classmethod
    def get_or_create_anonymous_user(cls):

        email = "anonymous@anonymous.cc"
        first_name = "anonymous"
        last_name = "anonymous"
        username = "anonymous"

        anonymous_user, created = cls.objects.get_or_create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        username=username
        )
        return anonymous_user

    @property
    def courses(self):
        from courses.models.course import Course
        return Course.objects.filter(created_by=self)

    @property
    def lectures(self):
        from courses.models.lecture import Lecture
        return Lecture.objects.filter(
        Q(created_by=self) | Q(teacher__user_id=self.id)
        )

class Student(models.Model):

    YEAR_IN_SCHOOL_CHOICES = [
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    ]
    ACADEMIC_YEAR = [
        (1, 'First'),
        (2, 'Second'),
        (3, 'Third'),
        (4, 'Fourth'),
        (5, 'Fifth'),
        (6, 'Sixth'),
        (7, 'Seventh'),
    ]
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    primary_key=True,
    related_name="student_profile"
    )
    major = models.CharField(blank=True, null=True, max_length=40)
    academic_year = models.IntegerField(blank=True, null=True, choices=ACADEMIC_YEAR)
    year_in_school = models.CharField(max_length=20, blank=True, null=True, choices=YEAR_IN_SCHOOL_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

    def is_enrolled(self, course):
        return course.id in self.user.enrollments.values_list('course', flat=True)

    def activate(self):
        if not self.is_active:
            self.is_active = False
            self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

class Teacher(models.Model):
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
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


# Model to store the list of logged in users
class LoggedInUser(models.Model):
    user = models.OneToOneField(User, related_name='logged_in_user', on_delete=models.CASCADE)
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.user.username
