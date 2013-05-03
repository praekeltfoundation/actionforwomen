from mama.sites.vlive.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mama.sqlite',                      # Or path to database file if using sqlite3.
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'snippetscream',
)

CREATE_DEFAULT_SUPERUSER = True

# Customizations allowing for dev testing through proxytunnel.
ROOT_URLCONF = 'mama.sites.vlive.urls_dev'
STATIC_URL = '/mama/static/'
MEDIA_URL = '/mama/media/'

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS += (
    'debug_toolbar',
)
