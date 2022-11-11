from django import forms
from django_currentuser.middleware import get_current_authenticated_user
from django.db import models
from courses.models import Course, CoursePricingPlan


class CoursePricingPlanForm(forms.ModelForm):

    class Meta:
        model = CoursePricingPlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CoursePricingPlanForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(created_by=get_current_authenticated_user())
