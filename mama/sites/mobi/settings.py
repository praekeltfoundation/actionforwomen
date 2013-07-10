from mama.settings import *

TEMPLATE_DIRS += (
    os.path.join(PATH, "mama", "templates", "mobi"),
    os.path.join(PATH, "survey", "templates", "mobi"),
)

CACHES['default']['KEY_PREFIX'] = 'mama_mobi'

LOGIN_REDIRECT_URL = '/survey/check-for-survey/'

INSTALLED_APPS += (
    'survey',
)

HOLODECK_URL = 'http://holodeck.praekelt.com/'
