from __future__ import absolute_import
import os
from os.path import dirname, join
import dotenv
from celery import Celery
from django.conf import settings

project_dir = dirname(dirname(__file__))
dotenv.read_dotenv(join(project_dir, '.env'))

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alteby.settings.' + os.environ.get('ENVIRONMENT'))
app = Celery('alteby')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
