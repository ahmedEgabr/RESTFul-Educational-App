from django.urls import path, include
from .views import ReferenceAutocomplete

app_name = 'courses'

urlpatterns = [
    path('references-autocomplete/', ReferenceAutocomplete.as_view(), name='references-autocomplete',),
  ]
