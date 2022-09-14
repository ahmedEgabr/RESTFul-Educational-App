from dal import autocomplete
from django_currentuser.middleware import get_current_authenticated_user
from django import forms
from courses.models import Course, Lecture, Topic
from users.models import Teacher
from categories.models import ReferenceCategory

class LectureForm(forms.ModelForm):
    reference_category = forms.ModelChoiceField(
    queryset=ReferenceCategory.objects.all(), required=False, label="Reference Category Filter"
    )
    course = forms.ModelChoiceField(
    queryset=Course.objects.filter(created_by=get_current_authenticated_user()), required=False, label="Course Topics Filter"
    )


    def __init__(self, *args, **kwargs):
        super(LectureForm, self).__init__(*args, **kwargs)
        self.fields['teacher'].disabled = True
        self.fields['teacher'].initial = get_current_authenticated_user().get_teacher_profile()

    class Meta:
        model = Lecture
        fields = (
        'title',
        'description',
        'objectives',
        'video',
        'audio',
        'script',
        'teacher',
        'reference_category',
        'references',
        )
        widgets = {
            'references': autocomplete.ModelSelect2Multiple(
            url='courses:references-autocomplete',
            forward=['reference_category']
            )
        }
