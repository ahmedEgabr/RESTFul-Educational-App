"""
Django settings for alteby project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from pathlib import Path
import os
import environ
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# reading .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
    'users.backends.CaseInsensitiveModelBackend'
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')


ALLOWED_HOSTS = [env('ALLOWED_HOST')]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'jazzmin',
    'alteby.admin_sites.MainAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'nested_inline',
    # 'admin_reorder',
    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
    'django_filters',
    'drf_yasg',
    'django_seed',
    'ckeditor',
    'django_countries',

    # APPS
    'main',
    'users',
    'teachers',
    'courses',
    'payment',
    'playlists',
    'categories'
]

# ADMIN_REORDER = (
#     # Keep original label and models
#     'auth',
#     'rest_framework',
#     'authtoken',
#     'users',
#     'playlists',
#     'categories',
#
#     # Reorder Courses models
#     {'app': 'courses', 'models': ('courses.Course', 'courses.Lecture', 'courses.CourseActivity', 'courses.Quiz', 'courses.QuizResult', 'courses.QuizAttempt')},
#
#     {'app': 'courses', 'label': 'Reports and Feedbacks' ,'models': ('courses.Report', 'courses.Feedback', 'courses.CorrectInfo', 'courses.Discussion')},
#
#     'payment'
# )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'alteby.middlewares.AssignUserGeoLocation',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'admin_reorder.middleware.ModelAdminReorder',
    'alteby.middleware.CoursePermissionMiddleware',
    # 'alteby.middlewares.TimezoneMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',

]

AUTH_EXEMPT_ROUTES = ('api')
ALLOWED_ENDPOINTS = ('signup', 'signin')

ROOT_URLCONF = 'alteby.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'alteby.wsgi.application'





# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Africa/Cairo"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'alteby.authentication.CustomTokenAuth',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER':'alteby.error_views.custom_exception_handler'
}

#Email BACKEND
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_USE_TLS = True
EMAIL_PORT = int(env('EMAIL_PORT'))
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_TIMEOUT = int(env('EMAIL_TIMEOUT')) #Time in seconds

# REST_FRAMEWORK Rest Password
DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    "CLASS": "django_rest_passwordreset.tokens.RandomStringTokenGenerator",
    "OPTIONS": {
        "min_length": 20,
        "max_length": 30
    }
}
DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 1 # Time in hours

# Django Admin
SITE_INDEX_TITLE = 'Emtyaz Advoisor'
SITE_TITLE = 'Administration'
SITE_HEADER = 'Emtyaz Advoisor'

BASE_PROTECTED_ROUTE ='api'
PROTECTED_ROUTE = 'courses'
ALLOWED_COURSE_ROUTES = ('index')
#
# import django_heroku
# django_heroku.settings(locals())

FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)

# CELERY SETTINGSS
BROKER_URL = env('BROKER_URL')
CELERY_RESULT_BACKEND = env('BROKER_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Cairo'

# CK Ediotor
CKEDITOR_UPLOAD_PATH = "ckeditor/"
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'office2013',
        'toolbar': 'full',
        'height': "100%",
        'width': "100%",
    },
}
