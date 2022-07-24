from dal import autocomplete
from django import forms
from courses.models import Lecture
from categories.models import ReferenceCategory

class LectureForm(forms.ModelForm):
    reference_category = forms.ModelChoiceField(queryset=ReferenceCategory.objects.all(),
                                    disabled=False, required=False, label="Reference category")
    class Meta:
        model = Lecture
        fields = (
        'topic',
        'title',
        'description',
        'objectives',
        'video',
        'audio',
        'script',
        'teacher',
        'quiz',
        'reference_category',
        'references',
        'order'
        )
        widgets = {
            'references': autocomplete.ModelSelect2Multiple(
            url='courses:references-autocomplete',
            forward=['reference_category']
            )
        }
