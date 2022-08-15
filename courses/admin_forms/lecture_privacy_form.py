from django import forms
from courses.models import Privacy, LecturePrivacy


class LecturePrivacyPriceForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        
        super(LecturePrivacyPriceForm, self).__init__(*args, **kwargs)
        self.fields['option'].choices = [
            option for option in Privacy.PRIVACY_CHOICES if option[0] != Privacy.PRIVACY_CHOICES.limited_duration
            ]
            
    class Meta:
        model = LecturePrivacy
        fields = '__all__'
