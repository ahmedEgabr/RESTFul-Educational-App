from dal import autocomplete
from django import forms
from courses.models import Lecture, Course
from categories.models import ReferenceCategory

class LectureForm(forms.ModelForm):
    reference_category = forms.ModelChoiceField(queryset=ReferenceCategory.objects.all(),
                                    disabled=False, required=False, label="Reference category")

    course = forms.ModelChoiceField(
    queryset=Course.objects.all(), required=False, label="Course Topics Filter"
    )

    class Meta:
        model = Lecture
        fields = (
        'course',
        'topic',
        'title',
        'description',
        'objectives',
        'video',
        'audio',
        'script',
        'teacher',
        'reference_category',
        'references',
        'order'
        )
        widgets = {
            'references': autocomplete.ModelSelect2Multiple(
            url='courses:references-autocomplete',
            forward=['reference_category']
            ),
            'topic': autocomplete.ModelSelect2(
            url='courses:topic-autocomplete',
            forward=['course']
            )
        }
