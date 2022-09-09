from dal import autocomplete
from django import forms
from courses.models import LectureOverlap, Course, Unit
from django_currentuser.middleware import get_current_authenticated_user


class LectureOverlapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LectureOverlapForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(created_by=get_current_authenticated_user())
        
    course = forms.ModelChoiceField(
    queryset=Course.objects.filter(created_by=get_current_authenticated_user()), required=False, label="Course Filter"
    )
    unit = forms.ModelChoiceField(
    queryset=Unit.objects.all(), 
    required=False, 
    label="Unit Filter", 
    widget=autocomplete.ModelSelect2(
            url='courses:units-autocomplete',
            forward=['course']
        )
    )

    class Meta:
        model = LectureOverlap
        fields = (
            'course',
            'unit',
            'topic',
            'order',
        )
        widgets = {
            'topic': autocomplete.ModelSelect2(
            url='courses:topics-autocomplete',
            forward=['unit']
            )
        }


