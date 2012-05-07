from mama.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mama.sqlite',                      # Or path to database file if using sqlite3.
    }
}

DEBUG=True
TEMPLATE_DEBUG=DEBUG
