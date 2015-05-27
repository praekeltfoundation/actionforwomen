from project.settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'app_test.sqlite',
    }
}

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True
