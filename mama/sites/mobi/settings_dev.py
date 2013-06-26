from mama.sites.mobi.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mama.sqlite',
    }
}

TEMPLATE_DIRS += (
    os.path.join(PATH, "survey", "templates", "mobi"),
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS += (
    'debug_toolbar',
    'survey',
)

# URL for a DEVELOPMENT Holodeck instance
HOLODECK_URL = 'http://localhost:8001/'
