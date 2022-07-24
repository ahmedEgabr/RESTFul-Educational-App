from django import forms
from django.db import models
from payment.models import CourseEnrollment
from courses.models import Course


class CourseEnrollmentForm(forms.ModelForm):

    class Meta:
        model = CourseEnrollment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CourseEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(created_by=get_current_authenticated_user())
