from mama.settings import *

TEMPLATE_DIRS = (
    os.path.join(PATH, "mama", "templates", "vlive"),
)

INSTALLED_APPS += (
    'pml',
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'pml.middleware.XMLResponseMiddleware',
    'pml.middleware.FormMiddleware',
    'pml.middleware.RedirectMiddleware',
    'pml.middleware.VLiveRemoteUserMiddleware',
    'pml.middleware.NoCacheMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'mama.sites.vlive.urls'