from mama.settings import *

TEMPLATE_DIRS += (
    os.path.join(PATH, "mama", "templates", "mobi"),
)

CACHES['default']['KEY_PREFIX'] = 'mama_mobi'
