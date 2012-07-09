from datetime import date, timedelta
from unittest import TestCase

from django.contrib.auth.models import User
from mama.models import UserProfile


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
