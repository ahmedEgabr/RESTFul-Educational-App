from django import forms
from django.db import models
from payment.models import CourseEnrollment
from courses.models import Course, Lecture, Topic
from users.models import User, Teacher
from django_currentuser.middleware import get_current_authenticated_user


class LectureForm(forms.ModelForm):

    class Meta:
        model = Lecture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LectureForm, self).__init__(*args, **kwargs)
        self.fields['topic'].queryset = Topic.objects.filter(created_by=get_current_authenticated_user())
        self.fields['teacher'].queryset = Teacher.objects.filter(user=get_current_authenticated_user())


class CourseEnrollmentForm(forms.ModelForm):

    class Meta:
        model = CourseEnrollment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CourseEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(created_by=get_current_authenticated_user())
