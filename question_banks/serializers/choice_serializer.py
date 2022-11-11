from rest_framework import serializers
from question_banks.models import Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'choice', 'is_correct', 'explanation', 'explanation')
