from mama.settings import *

TEMPLATE_DIRS += (
    os.path.join(PATH, "mama", "templates", "mobi"),
)

CACHES['default']['KEY_PREFIX'] = 'mama_mobi'

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
    'mama.middleware.TrackOriginMiddleware',
)
