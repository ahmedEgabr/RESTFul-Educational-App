from django import forms
from django_currentuser.middleware import get_current_authenticated_user
from django.db import models
from courses.models import Reference
from categories.models import ReferenceCategory


class ReferenceForm(forms.ModelForm):

    class Meta:
        model = Reference
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)
        self.fields['categories'].queryset = ReferenceCategory.objects.filter(created_by=get_current_authenticated_user())
