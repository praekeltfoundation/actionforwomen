from datetime import date, timedelta
from unittest import TestCase

from django.contrib.auth.models import User
from mama.models import UserProfile

from survey import constants
from survey.models import Questionnaire


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

    def test_survey_declined_option(self):
        """ Test the decline survey option
        """
        # create a questionnaire
        boss_man = User.objects.create(username='boss',
                                       password='bigsecret')
        boss_man.is_active = True
        boss_man.is_staff = True
        boss_man.is_superuser = True
        boss_man.save()

        questionnaire1 = Questionnaire.objects.create(
            title='MAMA Questionnaire',
            introduction_text='Intro text',
            thank_you_text='Thank you',
            created_by=boss_man,
            active=True)
        question1 = questionnaire1.multichoicequestion_set.create(
            question_order=0,
            question_text='Question 1')
        option1 = question1.multichoiceoption_set.create(
            option_order=0,
            option_text='Option 1',
            is_correct_option=False)
        option2 = question1.multichoiceoption_set.create(
            option_order=1,
            option_text='Option 2',
            is_correct_option=True)

        # create a user
        guinea_pig, created = User.objects.get_or_create(
            username='thepig3',
            password='dirtysecret3')
        guinea_pig.active = True
        guinea_pig.save()
        profile = UserProfile.objects.create(user=guinea_pig)
        profile.decline_surveys = True
        profile.save()

        # do the test
        self.assertIsNone(
            Questionnaire.objects.questionnaire_for_user(guinea_pig))

        profile.decline_surveys = False
        profile.save()

        # do the test
        self.assertEqual(
            Questionnaire.objects.questionnaire_for_user(guinea_pig),
            questionnaire1)
