from mama.settings import *

TEMPLATE_DIRS = (
    os.path.join(PATH, "mama", "templates", "vlive"),
)

INSTALLED_APPS += (
    'djcelery',
    'google_analytics',
    'pml',
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'pml.middleware.XMLResponseMiddleware',
    'pml.middleware.FormMiddleware',
    'pml.middleware.RedirectMiddleware',
    'pml.middleware.VLiveRemoteUserMiddleware',
    'pml.middleware.NoCacheMiddleware',
    'google_analytics.middleware.GoogleAnalyticsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'mama.sites.vlive.urls'
ROOT_URL = 'http://vlive.askmama.mobi/'

CACHES['default']['KEY_PREFIX'] = 'mama_vlive'

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'UA-40632967-1',
}

CELERY_IMPORTS = ('google_analytics.tasks')
