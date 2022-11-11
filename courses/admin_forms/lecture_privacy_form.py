from django import forms
from courses.models import Privacy, LecturePrivacy


class LecturePrivacyForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        
        super(LecturePrivacyForm, self).__init__(*args, **kwargs)
        
        allowed_privacy_choices = [
            Privacy.PrivacyType.PUBLIC,
            Privacy.PrivacyType.PRIVATE,
            Privacy.PrivacyType.SHARED,
        ]
        privacy_choices = [choice for choice in Privacy.PrivacyType.choices if choice[0] in allowed_privacy_choices]
        self.fields["option"].choices = privacy_choices
            
    class Meta:
        model = LecturePrivacy
        fields = '__all__'
