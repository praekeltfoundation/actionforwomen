from mama.settings import *

TEMPLATE_DIRS = (
    os.path.join(PATH, "mama", "templates", "mxit"),
)

CACHES['default']['KEY_PREFIX'] = 'mama_mxit'

ORIGIN = 'mxit'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mxit.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
    'mama.middleware.TrackOriginMiddleware',
    'google_analytics.middleware.GoogleAnalyticsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

GOOGLE_ANALYTICS_IGNORE_PATH = ['/health/', ]

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'MO-40632967-2',
}

CELERY_IMPORTS = ('google_analytics.tasks', 'monitor.tasks', 'moderator.tasks')

GA_CLIENT_ID = '643337966908-5bchse2iie7e0i6m15f5n9ttqquc13ov.apps.googleusercontent.com'
GA_CLIENT_SECRET = '42wRH_2YjBNdDNpYbFOGvmjy'
GA_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
GA_REDIRECT_URI = 'http://mxit.askmama.mobi/google-credentials/callback'
