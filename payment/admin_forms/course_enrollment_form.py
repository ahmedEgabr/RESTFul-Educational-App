from django import forms
from payment.models import CourseEnrollment


class CourseEnrollmentForm(forms.ModelForm):
        
    email = forms.CharField(required=False, disabled=True)
    username = forms.CharField(required=False, disabled=True)
    
    def __init__(self, *args, **kwargs):
        
        super(CourseEnrollmentForm, self).__init__(*args, **kwargs)
        self.initial["email"] = self.instance.user.email
        self.initial["username"] = self.instance.user.username
        

    class Meta:
        model = CourseEnrollment
        fields = "__all__"
