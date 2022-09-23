from dal import autocomplete
from django import forms
from courses.models import LectureOverlap, Course, Unit

class LectureOverlapForm(forms.ModelForm):
    
    course = forms.ModelChoiceField(
    queryset=Course.objects.all(), required=False, label="Course Filter"
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
    
    def __init__(self, *args, **kwargs):
        
        super(LectureOverlapForm, self).__init__(*args, **kwargs)
        if 'topic' in self.initial and self.initial["topic"]:
            self.initial["unit"] = self.instance.topic.unit
            self.initial["course"] = self.instance.topic.unit.course

