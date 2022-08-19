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
    'categories',
    'question_banks'
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
    'alteby.middlewares.TimezoneMiddleware',
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
    'PAGE_SIZE': 5,
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


JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Emtyaz Advoisor",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Emtyaz Advoisor",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Emtyaz Advoisor",

    # Welcome text on the login screen
    "welcome_sign": "Emtyaz Advisor Administration",

    # Copyright on the footer
    "copyright": "Emtyaz Advisor",

    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": "users.User",

    # #############
    # # Side Menu #
    # #############

    # Whether to display the side menu
    "show_sidebar": True,

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["main", "auth", "users", "courses", "courses.course", "courses.lecture", "courses.lecturequality"],

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth.Group": "fas fa-users",
        "users.User": "fas fa-fingerprint",
        "users.Teacher": "fas fa-solid fa-user-tie",
        "users.Student": "fas fa-solid fa-user-graduate",
        
        "main.AppStatus": "fas fa-wifi",
        "main.AppVersion": "fas fa-code-branch",
        "main.AppConfiguration": "fas fa-cogs",
        "main.ContactUs": "fas fa-address-card",
        
        "courses.Course": "fas fa-book-open",
        "courses.Lecture": "fab fa-youtube",
        "courses.LectureQuality": "fas fa-play",
        "courses.CorrectInfo": "fas fa-info-circle",
        "courses.CourseActivity": "fas fa-chart-bar",
        "courses.CoursePricingPlan":"fas fa-money-check-alt",
        "courses.Discussion": "fas fa-comments",
        "courses.Feedback": "fas fa-envelope",
        "courses.Note": "fas fa-sticky-note",
        "courses.QuizAttempt": "fas fa-undo",
        "courses.Reference": "fas fa-book-medical",
        "courses.Report": "fas fa-flag",
        
        "playlists.Favorite": "fas fa-heart",
        "playlists.Playlist": "fas fa-play-circle",
        "playlists.WatchHistory": "fas fa-history",
        
        "question_banks.Question": "fas fa-question-circle",
        "question_banks.QuestionResult": "fas fa-clipboard-check",

        
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,

}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-gray-dark navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    },
    "actions_sticky_top": True
}

# Abstract API
IP_GEO_URL = "https://ipgeolocation.abstractapi.com/v1/?api_key={0}&ip_address={1}"
IP_GEO_KEY = env('IP_GEO_KEY')
IP_GEO_WHITELISTED_VIEWS = [
    "CourseList",
    "FeaturedCoursesList",
    "CourseDetail", 
    "CoursePricingPlanList",
    ]