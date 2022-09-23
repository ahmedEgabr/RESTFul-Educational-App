from django import forms
from courses.models import PlanPrice


class PlanPriceForm(forms.ModelForm):
    class Meta:
        model = PlanPrice
        fields = '__all__'
