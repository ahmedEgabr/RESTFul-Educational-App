from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import ContactUs

main_admin.register(ContactUs)
