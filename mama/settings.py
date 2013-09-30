# Django settings for project project.

import os
import djcelery

PATH = os.getcwd()

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mama',
        'USER': 'mama',
        'PASSWORD': 'mama',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Africa/Johannesburg'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PATH, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "preferences.context_processors.preferences_cp",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
    'mama.middleware.TrackOriginMiddleware',
)

ROOT_URLCONF = 'mama.urls'
ROOT_URL = 'http://askmama.mobi'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = (
    'object_tools',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',

    'post',
    'mama',
    'category',
    'ckeditor',
    'export',
    'generate',
    'google_credentials',
    'haystack',
    'jmbo',
    'likes',
    'moderator',
    'photologue',
    'poll',
    'publisher',
    'preferences',
    'secretballot',
    'sites_groups',
    'south',
    'south_admin',
    'userprofile',
    'gunicorn',

    'survey',
    'monitor',
    'djcelery',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CKEDITOR_UPLOAD_PATH = os.path.join(PATH, 'media/uploads')

# Since we monkey-patch color field to category, override
# categories migration scripts with our own.
# Also preferences __module__ override requires our own migrations.
SOUTH_MIGRATION_MODULES = {
    'category': 'mama.migrations_category',
    'preferences': 'mama.migrations_preferences',
}

# NOTE: These now need to be the same value because we're using
#       `user.get_profile()` because it allows for easier mocking
USER_PROFILE_MODULE = AUTH_PROFILE_MODULE = 'mama.UserProfile'

# If no 'next' value found during login redirect home.
LOGIN_REDIRECT_URL = '/survey/check-for-survey/'

HOLODECK_URL = 'http://holodeck.praekelt.com/'

HAYSTACK_SITECONF = 'mama.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PATH, 'whoosh.index')

EMAIL_SUBJECT_PREFIX = '[MAMA] '

AMBIENT_API_KEY = ''
AMBIENT_GATEWAY_PASSWORD = ''

MODERATOR = {
    'CLASSIFIER': 'moderator.storage.RedisClassifier',
    'CLASSIFIER_CONFIG': {
        'host': 'localhost',
        'port': 6379,
        'db': 8,
        'password': None,
        'socket_timeout': None,
        'connection_pool': None,
        'charset': 'utf-8',
        'errors': 'strict',
        'unix_socket_path': None,
    },
    'HAM_CUTOFF': 0.3,
    'SPAM_CUTOFF': 0.7,
    'ABUSE_CUTOFF': 3,
}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Set session cookie age to 1 year, meaning sessions are
# valid for up to 1 year.
SESSION_COOKIE_AGE = 31536000

GA_CLIENT_ID = ''
GA_CLIENT_SECRET = ''
GA_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
GA_REDIRECT_URI = 'http://askmama.mobi/google-credentials/callback'

SERIALIZATION_MODULES = {
    'csv': 'snippetscream.csv_serializer',
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    }
}

ORIGIN = 'mobi'

# Puppet will put this on the server.
try:
    from production_settings import *
except ImportError:
    pass


SECRET_KEY = '1'

# Celery configuration options
BROKER_URL = 'amqp://guest:guest@localhost:5672/'

CELERY_RESULT_BACKEND = "database"
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Uncomment if you're running in DEBUG mode and you want to skip the broker
# and execute tasks immediate instead of deferring them to the queue / workers.
# CELERY_ALWAYS_EAGER = DEBUG

# Tell Celery where to find the tasks
# CELERY_IMPORTS = ('celery_app.tasks',)

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'login-every-24-hours': {
        'task': 'monitor.tasks.run_tasks',
        'schedule': timedelta(hours=24),
    },
}

# Defer email sending to Celery, except if we're in debug mode,
# then just print the emails to stdout for debugging.
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

SENDER = ""
RECIPIENT = ["", ""]

# This stores all the settings that will be used in the api
HOTSOCKET_BASE = "http://api.hotsocket.co.za:8080/"

HOTSOCKET_RESOURCES = {
    "login": "login",
    "recharge": "recharge",
    "status": "status",
    "statement": "statement",
    "balance": "balance",
}

HOTSOCKET_USERNAME = ""
HOTSOCKET_PASSWORD = ""

TOKEN_DURATION = 110  # Minutes


HOTSOCKET_CODES = {
    "SUCCESS": {"status": "0000", "message": "Successfully submitted recharge."},
    "TOKEN_INVALID": {"status": 887, "message": "Token is invalid , please login again to obtain a new one."},
    "TOKEN_EXPIRE": {"status": 889, "message": "Token has timed out , please login again to obtain a new one."},
    "MSISDN_NON_NUM": {"status": 6013, "message": "Recipient MSISDN is not numeric."},
    "MSISDN_MALFORMED": {"status": 6014, "message": "Recipient MSISDN is malformed."},
    "PRODUCT_CODE_BAD": {"status": 6011, "message": "Unrecognized product code, valid codes are AIRTIME, DATA, and SMS."},
    "NETWORK_CODE_BAD": {"status": 6012, "message": "Unrecognized network code."},
    "COMBO_BAD": {"status": 6020, "message": " Network code + Product Code + Denomination combination is invalid."},
    "REF_DUPLICATE": {"status": 6016, "message": "Reference must be unique."},
    "REF_NON_NUM": {"status": 6017, "message": "Reference must be a numeric value."},
}

HS_RECHARGE_STATUS_CODES = {
    "PENDING": {"code": 0 },
    "PRE_SUB_ERROR": {"code": 1},
    "FAILED": {"code": 2},
    "SUCCESS": {"code": 3},
}
