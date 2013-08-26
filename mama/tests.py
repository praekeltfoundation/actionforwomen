from datetime import date, timedelta
from unittest import TestCase

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.conf import settings

from mama.models import UserProfile
from mama.middleware import TrackOriginMiddleware


class ProfileTestCase(TestCase):
    def test_is_prenatal(self):
        user = User.objects.create()
        profile = UserProfile.objects.create(user=user)

        self.failUnlessEqual(
            profile.is_prenatal(),
            True,
            "Without delivery_date set profile is considered "
            "prenatal, is_prenatal should be True"
        )
        self.failUnlessEqual(
            profile.is_postnatal(),
            False,
            "Without delivery_date set profile is considered prenatal, "
            "is_postnatal should be False"
        )

        profile.delivery_date = date.today() + timedelta(days=10)
        profile.save()
        self.failUnless(profile.delivery_date)
        self.failUnlessEqual(
            profile.is_prenatal(),
            True,
            "With delivery_date set in future is_prenatal should be True"
        )
        self.failUnlessEqual(
            profile.is_postnatal(),
            False,
            "With delivery_date set in future is_postnatal should be False"
        )

        profile.delivery_date = date.today() - timedelta(days=10)
        profile.save()
        self.failUnless(profile.delivery_date)
        self.failUnlessEqual(
            profile.is_prenatal(),
            False,
            "With delivery_date set in past is_prenatal should be False"
        )
        self.failUnlessEqual(
            profile.is_postnatal(),
            True,
            "With delivery_date set in past is_postnatal should be True"
        )


class TrackOriginMiddlewareTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        self.mw = TrackOriginMiddleware()

    def test_process_request(self):
        self.assertEqual(self.user.profile.origin, None)
        request_factory = RequestFactory()
        request = request_factory.get('/path', data={'name': u'test'})
        request.user = self.user
        self.mw.process_request(request)
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.origin, settings.ORIGIN)
