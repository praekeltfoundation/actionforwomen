from mama.settings import *
import djcelery
djcelery.setup_loader()

TEMPLATE_DIRS = (
    os.path.join(PATH, "mama", "templates", "vlive"),
)

INSTALLED_APPS += (
    'djcelery',
    'google_analytics',
    'pml',
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'pml.middleware.VLiveRemoteUserMiddleware',
    'pml.middleware.XMLResponseMiddleware',
    'pml.middleware.FormMiddleware',
    'pml.middleware.RedirectMiddleware',
    'pml.middleware.NoCacheMiddleware',
    'likes.middleware.SecretBallotUserIpUseragentMiddleware', #This also needs to be included after the remote user middleware
    'mama.middleware.TrackOriginMiddleware',
    'google_analytics.middleware.GoogleAnalyticsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ORIGIN = 'vlive'

ROOT_URLCONF = 'mama.sites.vlive.urls'
ROOT_URL = 'http://vlive.askmama.mobi'

CACHES['default']['KEY_PREFIX'] = 'mama_vlive'

PML_IGNORE_PATH = ['/djga/', '/google-credentials/', ]
GOOGLE_ANALYTICS_IGNORE_PATH = ['/health/', ]

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'MO-40632967-1',
}

CELERY_IMPORTS = ('google_analytics.tasks', 'monitor.tasks', 'moderator.tasks')

GA_CLIENT_ID = '366062914538.apps.googleusercontent.com'
GA_CLIENT_SECRET = 'P1wntBIm3hDNpuZZQvavzz3U'
GA_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
GA_REDIRECT_URI = 'http://vlive.askmama.mobi/google-credentials/callback'
