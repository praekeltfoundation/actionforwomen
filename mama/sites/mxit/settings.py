from mama.settings import *

TEMPLATE_DIRS += (
    os.path.join(PATH, "mama", "templates", "mxit"),
)

CACHES['default']['KEY_PREFIX'] = 'mama_mxit'
