from django.urls import path, include
from .views import ReferenceAutocomplete, TopicAutocomplete

app_name = 'courses'

urlpatterns = [
    path('references-autocomplete/', ReferenceAutocomplete.as_view(), name='references-autocomplete',),
    path('topic-autocomplete/', TopicAutocomplete.as_view(), name='topic-autocomplete',),
  ]
