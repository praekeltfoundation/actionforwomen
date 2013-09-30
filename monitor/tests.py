from django.test import TestCase
from mock import patch
import requests
from monitor.tasks import hotsocket_login
from django.test.utils import override_settings
from django.conf import settings


class TestHotSocketAPi(TestCase):
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS = True,
                       CELERY_ALWAYS_EAGER = True,
                       BROKER_BACKEND = 'memory',)

    def test_login_to_API(self):
        data = {
                "username": settings.HOTSOCKET_USERNAME,
                "password": settings.HOTSOCKET_PASSWORD,
                "as_json": True
            }
        url = "%s%s" % (settings.HOTSOCKET_BASE, settings.HOTSOCKET_RESOURCES["login"])

        with patch.object(requests, 'post') as mock_login:
            hotsocket_login()
            mock_login.assert_called_once_with(url, data=data)


