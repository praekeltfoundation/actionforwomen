from datetime import date, timedelta, time
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.test.client import Client
from django.conf import settings
from django.utils.crypto import salted_hmac
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.contrib import comments
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.management import call_command
from StringIO import StringIO
import sys

Comment = comments.get_model()
from datetime import datetime
from dateutil.relativedelta import *
from mama import utils
from mama.models import UserProfile
from mama.middleware import TrackOriginMiddleware
from mama.models import SitePreferences
from preferences import preferences
from post.models import Post
from category.models import Category

def generate_security_hash(content_type, object_pk, timestamp):
    info = (content_type, str(object_pk), str(timestamp))
    key_salt = "django.contrib.forms.CommentSecurityForm"
    value = "-".join(info)
    return salted_hmac(key_salt, value).hexdigest()


def params_for_comments(obj, comment):
    content_type = '%s.%s' % (obj._meta.app_label, obj._meta.module_name)
    object_pk = obj.pk

    timestamp = "1" * 40
    return {
        'content_type': content_type,
        'object_pk': object_pk,
        'timestamp': timestamp,
        'security_hash': generate_security_hash(content_type, object_pk,
                                                timestamp),
        'comment': comment
    }


class ProfileTestCase(TestCase):
    def setUp(self):
        '''
        These are required for Vlive
        '''
        #self.msisdn = '27123456789'
        #self.client = Client(HTTP_X_UP_CALLING_LINE_ID=self.msisdn)
        #self.client.login(remote_user=self.msisdn)

    def test_mobi_register_with_due_date(self):
        # make sure the client is logged out
        self.client.logout()

        # browse to the registration url
        resp = self.client.get(reverse('registration_register'))
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, 'Are you a..')

        # Test Empty and Unknown Due Date registration

        # 1. Test empty due date
        post_data = {
            'username': 'test_due',
            'password1': '1234',
            'mobile_number': '0712341111',
            'relation_to_baby':'mom_or_mom_to_be',
            'date_qualifier':'due_date',
            'due_date_month':0,
            'due_date_day':0,
            'due_date_year':0,
            'tos': True
        }

        resp = self.client.post(reverse('registration_register'), post_data)
        self.assertContains(resp, 'Either provide a due date, or check')

        # 2. Test unknown due date
        post_data.update({
            'unknown_date': True,
        })
        resp = self.client.post(reverse('registration_register'),
                                post_data,
                                follow=True)
        self.assertRedirects(resp,
                             reverse('registration_done'),
                             status_code=302,
                             target_status_code=200)
        self.assertContains(resp, 'Thank you for joining MAMA')

        # 2a. Go to the profile page to check the data
        resp = self.client.get(reverse('view_my_profile'))
        self.assertContains(resp, '0712341111')
        self.assertContains(resp, 'Due Date')
        self.assertContains(resp, 'Unknown')

        # 2b. Check the home page for a due date form
        resp = self.client.get(reverse('home'))
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, 'entered a due date yet. Please enter one')

        # 2c. Fill in the due date and check for stage based info
        due_date = date.today() + timedelta(weeks=2)
        post_data = {
            'due_date_day': due_date.day,
            'due_date_month': due_date.month,
            'due_date_year': due_date.year
        }
        resp = self.client.post(reverse('update_due_date'),
                                post_data,
                                follow=True)
        self.assertRedirects(resp,
                             reverse('home'),
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(resp.status_code, 200)
        # check for the date on the profile page
        resp = self.client.get(reverse('view_my_profile'))
        self.assertContains(resp, '0712341111')
        self.assertContains(resp, 'Due Date')
        self.assertContains(resp, due_date.strftime('%d %b %Y'))

        self.client.logout()


        # Test known due date registration
        post_data = {
            'username': 'test_due_known',
            'password1': '1234',
            'mobile_number': '0712341112',
            'relation_to_baby':'mom_or_mom_to_be',
            'date_qualifier':'due_date',
            'due_date_month': due_date.month,
            'due_date_day': due_date.day,
            'due_date_year': due_date.year,
            'tos': True
        }
        resp = self.client.post(reverse('registration_register'),
                                post_data,
                                follow=True)
        self.assertRedirects(resp,
                             reverse('registration_done'),
                             status_code=302,
                             target_status_code=200)
        self.assertContains(resp, 'Thank you for joining MAMA')
        # check for the date on the profile page
        resp = self.client.get(reverse('view_my_profile'))
        self.assertContains(resp, '0712341112')
        self.assertContains(resp, 'Due Date')
        self.assertContains(resp, due_date.strftime('%d %b %Y'))

        self.client.logout()

    def test_mobi_register_with_birth_date(self):
        # Test birth date registration
        self.client.logout()
        birth_date = date.today() - timedelta(weeks=6)

        post_data = {
            'username': 'test_birth',
            'password1': '1234',
            'mobile_number': '0712341113',
            'relation_to_baby':'mom_or_mom_to_be',
            'date_qualifier':'birth_date',
            'delivery_date_month': birth_date.month,
            'delivery_date_day': birth_date.day,
            'delivery_date_year': birth_date.year,
            'tos': True
        }
        resp = self.client.post(reverse('registration_register'),
                                post_data,
                                follow=True)
        self.assertRedirects(resp,
                             reverse('registration_done'),
                             status_code=302,
                             target_status_code=200)
        self.assertContains(resp, 'Thank you for joining MAMA')
        # check for the date on the profile page
        resp = self.client.get(reverse('view_my_profile'))
        self.assertContains(resp, '0712341113')
        self.assertContains(resp, 'Birth Date')
        self.assertContains(resp, birth_date.strftime('%d %b %Y'))

        self.client.logout()

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


class GeneralPrefrencesTestCase(TestCase):

    def setUp(self):
        site = Site.objects.get_current()
        category = Category.objects.create(title='articles', slug='articles')
        self.post = Post.objects.create(title='Test', state='published')
        self.post.primary_category = category
        self.post.sites.add(site)
        self.post.save()

    def test_commenting_times_morning_to_evening(self):
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)

        pref.commenting_time_on = time(9, 0, 0)
        pref.commenting_time_off = time(22, 0, 0)
        pref.save()

        self.assertFalse(preferences.SitePreferences.comments_open(time(5,0,0)))
        self.assertFalse(preferences.SitePreferences.comments_open(time(23,30,0)))
        self.assertTrue(preferences.SitePreferences.comments_open(time(11,0,0)))
        self.assertTrue(preferences.SitePreferences.comments_open(time(21,59,59)))

    def test_commenting_times_evening_to_morning(self):
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)

        pref.commenting_time_on = time(22, 0, 0)
        pref.commenting_time_off = time(9, 0, 0)
        pref.save()

        self.assertFalse(preferences.SitePreferences.comments_open(time(10,0,0)))
        self.assertFalse(preferences.SitePreferences.comments_open(time(20,30,0)))
        self.assertTrue(preferences.SitePreferences.comments_open(time(22,30,0)))
        self.assertTrue(preferences.SitePreferences.comments_open(time(8,59,59)))

    def test_comment_views(self):
        #Page detail should show detail page with comment form
        article_url = reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        resp = self.client.get(article_url)
        self.assertNotContains(resp, 'Comments are closed.')

        #Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.save()
        c = Client()
        c.login(username='foo',password='foo')

        #Comment should be submitted successfully
        params = params_for_comments(self.post, 'sample comment')
        resp = c.post(reverse('post_comment'), params)
        self.assertEqual(Comment.objects.all().count(), 1)


        #ensure commenting closed
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.commenting_time_on = time(23, 59, 59)
        pref.commenting_time_off = time(0, 0, 1)
        pref.save()

        #clear cache for comments_open context processor
        cache.clear()

        #Comments should be closed
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp, 'Comments are currently closed.')

        #Comment post should fail
        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 400)

        self.assertEqual(Comment.objects.all().count(), 1)

    def test_accept_new_terms(self):
        #Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.save()
        c = Client()
        c.login(username='foo',password='foo')

        #ensure user is prompted to accept terms
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp, 'Want to comment? You will need to accept our new commenting rules first.')

        #agree to terms
        c.post(reverse('agree_comment'))
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))

        #Check agree terms message is gone
        self.assertNotContains(resp,'Want to comment? You will need to accept our new commenting rules first.')

    def test_report_user(self):
        #post unsafe comment
        params = params_for_comments(self.post, 'sample unsafe comment')
        self.client.post(reverse('post_comment'), params)

        #Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.save()
        c = Client()
        c.login(username='foo',password='foo')

        #report user
        c.get(reverse('confirm_comment',kwargs={'content_type':'Post','id':1}))
        c.post(reverse('report_comment',kwargs={'content_type':'Post','id':1,'vote':-1}))

        #check comment banned
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp,'This comment has been reported by the community and the user has been banned')

    def test_banned_user_comment(self):
        #Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.save()
        c = Client()
        c.login(username='foo',password='foo')

        #check user can comment
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertNotContains(resp, 'Want to comment? You will need to accept our new commenting rules first.')
        self.assertNotContains(resp, 'You are banned from commenting')

        #ban user
        utils.ban_user(user, 1)

        #check user cannot comment
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp, 'You are banned from commenting')


    def test_unban_user(self):
        #Create banned and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.banned = True
        profile.last_banned_date = date.today() - timedelta(days=1)
        profile.ban_duration = 1
        profile.save()
        c = Client()
        c.login(username='foo',password='foo')

        #check user cannot comment
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp, 'You are banned from commenting')

        #unban user
        utils.unban_user(user)

        #check user can comment
        resp = c.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertNotContains(resp, 'You are banned from commenting')

    def test_banned_words(self):
        article_url = reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_banned_patterns = 'crap\ndoodle'
        pref.save()

        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

        params = params_for_comments(self.post, 'some comment with crap')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertContains(resp, 'inappropriate content')

    def test_silenced_words(self):
        article_url = reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_silenced_patterns = 'doodle'
        pref.save()

        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

        params = params_for_comments(self.post, 'some doodle with crap')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get(article_url)
        self.assertContains(resp, 'some ****** with crap')

    def test_invalid_banned_words(self):
        article_url = reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_banned_patterns = 'crap\ndoodle\n' #contains blank line
        pref.save()

        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

    def test_invalid_silenced_words(self):
        article_url = reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_silenced_patterns = 'crap\ndoodle\n'
        pref.save()

        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

    def test_regex_patterns(self):
        article_url = reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_banned_patterns = 'crap\ndoodle\nf**k'
        pref.comment_silenced_patterns = 'monkey'
        pref.save()

        params = params_for_comments(self.post, 'some comment with f**k word')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertContains(resp, 'inappropriate content')

        params = params_for_comments(self.post, 'some comment with CRAP in caps')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertContains(resp, 'inappropriate content')

        params = params_for_comments(self.post, 'word MONKEY which is silenced')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get(article_url)
        self.assertContains(resp, 'word ****** which is silenced')


    def test_times(self):

        #Simulate a monday and test true
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(0, now=datetime.now() + relativedelta(weekday=MO(-1),
                                       hour=0, minute=0,
                                       second=0, microsecond=0))

        self.assertTrue(can_vote)
        self.assertGreater(end_thursday, start_friday)

        #Simulate a wednesday and test false
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(0, now=datetime.now() + relativedelta(weekday=WE(-1),
                                       hour=0, minute=0,
                                       second=0, microsecond=0))

        self.assertFalse(can_vote)
        self.assertGreater(end_thursday, start_friday)

        #Simulate a monday and test true a week ago
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(1, now=datetime.now() + relativedelta(weekday=MO(-1),
                                       hour=0, minute=0,
                                       second=0, microsecond=0))

        self.assertTrue(can_vote)
        self.assertGreater(end_thursday, start_friday)

        #Simulate a wednesday and test false a week ago
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(1, now=datetime.now() + relativedelta(weekday=WE(-1),
                                       hour=0, minute=0,
                                       second=0, microsecond=0))

        self.assertFalse(can_vote)
        self.assertGreater(end_thursday, start_friday)


class MobileNumberInternationlisationTestCase(TestCase):
    def test_mobile_number_internationalisation(self):
        num = utils.mobile_number_to_international('27123456789')
        self.assertEqual(num, '27123456789')

        num = utils.mobile_number_to_international('0123456789')
        self.assertEqual(num, '27123456789')


class SendStageMessagesTestCase(TestCase):

    def setUp(self):

        self.mock_html = u'''
        <p>This is a paragraph<br />
    Some More text Some More text</p>
    <p>This is paragraph 2<br />
    <br />
Some More text Some <b>More text</b> Some More text<br />
Some More text Some <i>More</i> text Some More text</p>
<div>
<p>Some More text Some More text</p>
<p>Some More text Some More text Some More text<br />
<br />
    Some More text Some More text Some More text</p>
    </div>
'''

        self.mock_clean = u'''This is a paragraph

Some More text Some More text

This is paragraph 2

Some More text Some More text Some More text

Some More text Some More text Some More text

Some More text Some More text

Some More text Some More text Some More text

Some More text Some More text Some More text'''

    def test_send_stage_based_messages(self):

        """Test 'sendstagemessages' command"""

        sys_output = sys.stdout
        sys.stdout = output = StringIO()

        call_command('sendstagemessages')

        sys.stdout = sys_output

        output.seek(0)  # Start reading from the beginning

        #Make sure it reaches the end of file
        self.assertIn('Done!', output.read())
        output.seek(0)
        # Make sure that we get a response
        self.assertIsNotNone(output.read())

    def test_string_formatting(self):
        clean_string = utils.format_html_string(self.mock_html)

        # Assert that we get a proper value back and that it has
        # been parsed (assert!=)
        self.assertTrue(clean_string)
        self.assertNotEqual(self.mock_html, clean_string)
        self.assertNotIn('\r', clean_string)
        self.assertEqual(self.mock_clean, clean_string)

        clean_string = utils.format_html_string(u'')

        # Assert that we don't get unexpected input when we pass in False values
        self.assertFalse(clean_string)
