# Django settings for project project.

import os
import djcelery
djcelery.setup_loader()

PATH = os.getcwd()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'actionforwomen',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
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
    "livechat.context_processors.current_livechat",
    "app.context_processors.comments_open",
    "app.context_processors.read_only_mode",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'apptemplates.Loader',
)

MIDDLEWARE_CLASSES = (
    # NOTE: this is a very aggresive middleware that rejects everything
    #       that isn't a GET or a HEAD request.
    # 'app.middleware.ReadOnlyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
    'app.middleware.TrackOriginMiddleware',
)

ROOT_URLCONF = 'app.urls'
ROOT_URL = 'http://actionforwomen.mobi'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
    os.path.join(os.path.dirname(__file__), "templates", "app", "mobi"),
)

INSTALLED_APPS = (
    'object_tools',
    'moderator',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jmbo',
    'django_nose',
    'post',
    'app',
    'category',
    'ckeditor',
    'export',
    'generate',
    'google_credentials',
    'haystack',
    'likes',
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
    'jmboyourwords',
    'livechat',
    'app.commenting',
    'djcelery',
    'google_analytics',
    'raven.contrib.django.raven_compat',
)

COMMENTS_APP = 'app.commenting'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(PATH, 'logs/app.messages.log'),
            'formatter': 'verbose',
            'when': 'W0'  # rotate log every Monday
        },
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

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            ['Undo', 'Redo',
              '-', 'Bold', 'Italic', 'Underline', 'RemoveFormat'
            ],
            ['-', 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord',
              '-', 'Unlink',
              '-', 'Source',
            ]
        ],
        'forcePasteAsPlainText': True,
    }
}

# Since we monkey-patch color field to category, override
# categories migration scripts with our own.
# Also preferences __module__ override requires our own migrations.
SOUTH_MIGRATION_MODULES = {
    'category': 'app.migrations_category',
    'preferences': 'app.migrations_preferences',
}

# NOTE: These now need to be the same value because we're using
#       `user.get_profile()` because it allows for easier mocking
USER_PROFILE_MODULE = AUTH_PROFILE_MODULE = 'app.UserProfile'

# New login and logout urls as set in app.urls
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

# If no 'next' value found during login redirect home.
LOGIN_REDIRECT_URL = '/survey/check-for-survey/'

HOLODECK_URL = 'http://holodeck.praekelt.com/'

HAYSTACK_SITECONF = 'app.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PATH, 'whoosh.index')

EMAIL_SUBJECT_PREFIX = '[actionforwomen] '

VUMI_ACCOUNT_KEY = ''
VUMI_ACCESS_TOKEN = ''
VUMI_SMS_CONVERSATION_KEY = ''

LIVECHAT_PRIMARY_CATEGORY = 'ask-mama'
LIVECHAT_CATEGORIES = ('live-chat',)

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

SERIALIZATION_MODULES = {
    'csv': 'snippetscream.csv_serializer',
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'mobi',
    }
}

ORIGIN = 'mobi'

# Celery configuration options
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_IMPORTS = ('moderator.tasks')
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Uncomment if you're running in DEBUG mode and you want to skip the broker
# and execute tasks immediate instead of deferring them to the queue / workers.
# CELERY_ALWAYS_EAGER = DEBUG
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']

# Defer email sending to Celery, except if we're in debug mode,
# then just print the emails to stdout for debugging.
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

SENDER = ""
RECIPIENT = []

# This disables all POST operations on the site.
READ_ONLY_MODE = False

FROM_EMAIL_ADDRESS = "ActionForWomen<contact@actionforwomen.mobi>"

# Puppet will put this on the server.
try:
    from project.local_settings import *
except ImportError:
    pass
