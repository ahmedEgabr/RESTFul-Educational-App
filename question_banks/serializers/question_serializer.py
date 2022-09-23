from rest_framework import serializers
from question_banks.models import Question
from .choice_serializer import ChoiceSerializer


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ('id', 'reference', 'title', 'choices', 'extra_info', 'image')
