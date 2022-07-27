from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS +=[
    # this for debugging SQL
    'debug_toolbar',
    'silk'
]

MIDDLEWARE += [
    # For debugging
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'silk.middleware.SilkyMiddleware',
]

# This for degugging
INTERNAL_IPS = [
    env('ALLOWED_HOST'),
]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + env('DATABASE_ENGINE'),
        'NAME': env("DATABASE_NAME")
    }
}

# SILK CONFIG
SILKY_PYTHON_PROFILER = True 
