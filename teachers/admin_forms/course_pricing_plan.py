from django import forms
from django_currentuser.middleware import get_current_authenticated_user
from courses.models import Course, CoursePlan


class CoursePlanForm(forms.ModelForm):

    class Meta:
        model = CoursePlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CoursePlanForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(created_by=get_current_authenticated_user())
