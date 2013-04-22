from mama.settings import *

TEMPLATE_DIRS = (
    os.path.join(PATH, "mama", "templates", "vlive"),
)

INSTALLED_APPS += (
    'pml',
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'mama.middleware.PMLMiddleware',
    'mama.middleware.PMLFormMiddleware',
    'pml.middleware.RedirectMiddleware',
    'pml.middleware.VLiveRemoteUserMiddleware',
)