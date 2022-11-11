from django.urls import path
from .views import ContactUsView, AppVersionView
from courses.api.views import SearchView


app_name = 'main'

urlpatterns = [
    path('contactus', ContactUsView.as_view(), name='contactus'),
    path('check-app-status', AppVersionView.as_view(), name='check-app-status'),
    path('search/', SearchView.as_view(), name='search'),
  ]
