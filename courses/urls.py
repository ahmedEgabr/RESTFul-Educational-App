from django.urls import path, include
from .views import ReferenceAutocomplete, TopicsAutocomplete, UnitsAutocomplete

app_name = 'courses'

urlpatterns = [
    path('references-autocomplete/', ReferenceAutocomplete.as_view(), name='references-autocomplete',),
    path('units-autocomplete/', UnitsAutocomplete.as_view(), name='units-autocomplete',),
    path('topics-autocomplete/', TopicsAutocomplete.as_view(), name='topics-autocomplete',),
  ]
