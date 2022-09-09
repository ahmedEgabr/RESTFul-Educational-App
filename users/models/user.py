from django.db import models, transaction
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import Group
from alteby.constants import TEACHER_GROUP, STUDENT_GROUP, PROMOTER_GROUP
from main.models import AppConfiguration
from users.managers import UserManager
from django_countries.fields import CountryField
from .student import Student
from .teacher import Teacher

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
    is_promoter = models.BooleanField('Promoter status', default=False)
    screenshots_taken = models.IntegerField(
    blank=True, null=True, default=0, validators=[MinValueValidator(0)], verbose_name="Screenshots Taken"
    )
    country = CountryField(blank=True, blank_label='(select country)')

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

    def add_to_promoter_group(self):
        promoter_group, created = Group.objects.get_or_create(name=PROMOTER_GROUP)
        transaction.on_commit(lambda: self.groups.add(promoter_group))
        return True
    
    def remove_from_promoter_group(self):
        promoter_group = Group.objects.filter(name=PROMOTER_GROUP).first()
        if not promoter_group:
            return False
        transaction.on_commit(lambda: self.groups.remove(promoter_group))
        return True
    
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
    def courses_created(self):
        from courses.models.course import Course
        return Course.objects.filter(created_by=self)

    @property
    def lectures_created(self):
        from courses.models.lecture import Lecture
        return Lecture.objects.filter(
        Q(created_by=self) | Q(teacher__user_id=self.id)
        )
    
    def get_enrolled_courses(self):
        enrolled_courses_ids = self.enrollments.filter(
            Q(lifetime_enrollment=True) |
            Q(expiry_date__gt=timezone.now()),
            force_expiry=False,
            is_active=True
        ).values_list('course', flat=True)
        
        if not enrolled_courses_ids:
            return self.enrollments.none()
        
        from courses.models.course import Course
        return Course.objects.filter(id__in=enrolled_courses_ids)