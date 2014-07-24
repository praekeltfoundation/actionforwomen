from mama.settings import *

TEMPLATE_DIRS += (
    os.path.join(PATH, "mama", "templates", "zambia"),
    os.path.join(PATH, "mama", "templates", "unicore"),
    os.path.join(PATH, "mama", "templates", "mobi"),
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
    'mama.middleware.TrackOriginMiddleware',
)

CACHES['default']['KEY_PREFIX'] = 'mama_unicore_zambia'

ORIGIN = 'unicore_zambia'
SITE_ID = 2

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'UA-40632967-3',
}
