DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'app_test.sqlite',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',

    'app',
    'category',
    'jmbo',
    'photologue',
    'publisher',
    'secretballot',
    'userprofile',
)

STATIC_URL = ''

USER_PROFILE_MODULE = 'app.UserProfile'
