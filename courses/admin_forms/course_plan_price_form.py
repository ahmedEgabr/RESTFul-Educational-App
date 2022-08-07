from django import forms
from courses.models import CoursePlanPrice


class CoursePlanPriceForm(forms.ModelForm):
    class Meta:
        model = CoursePlanPrice
        fields = '__all__'
