from datetime import date, timedelta, time
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.conf import settings
from django.utils.crypto import salted_hmac
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.contrib import comments
from django.core.management import call_command
from StringIO import StringIO
import sys

Comment = comments.get_model()
from datetime import datetime
from dateutil.relativedelta import *
from app import utils
from app import tasks
from app.models import UserProfile, BanAudit
from app.middleware import TrackOriginMiddleware, ReadOnlyMiddleware
from app.context_processors import read_only_mode
from app.models import SitePreferences
from preferences import preferences
from post.models import Post
from category.models import Category
from app.forms import RegistrationForm, EditProfileForm

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
        # self.client.login(remote_user=self.msisdn)
        Site.objects.create(id=2, name='french', domain='fr.site.com')
        self.user = User.objects.create_user('test@email.com', 'test@email.com', '1234')

    def test_mobi_register_domestic_format(self):
        self.client.logout()

        post_data = {
            'username': 'an@email.com',
            'password1': '1234',
            'mobile_number': '231-456-7890',
            'email': 'an@email.com',
            'alias': '',
            'gender': '',
            'year_of_birth': '1989',
            'identity': '',
            'tos': True
        }

        resp = self.client.post(reverse('registration_register'),
                                post_data,
                                follow=True)
        # print 'resp', resp
        self.assertRedirects(resp,
                             reverse('registration_done'),
                             status_code=302,
                             target_status_code=200)
        self.assertContains(resp, 'Thank you for joining A4W')
        # check for the date on the profile page
        resp = self.client.get(reverse('view_my_profile'))
        self.assertContains(resp, '231-456-7890')

        self.client.logout()

    def test_mobi_register_international_format(self):
        self.client.logout()

        post_data = {
            'username': 'an@email.com',
            'password1': '1234',
            'mobile_number': '1-123-456-7890',  # Canadian numbers start with 1
            'email': 'an@email.com',
            'alias': '',
            'gender': '',
            'year_of_birth': '1989',
            'identity': '',
            'tos': True
        }

        resp = self.client.post(reverse('registration_register'),
                                post_data,
                                follow=True)
        # print 'resp', resp
        self.assertRedirects(resp,
                             reverse('registration_done'),
                             status_code=302,
                             target_status_code=200)
        self.assertContains(resp, 'Thank you for joining A4W')
        # check for the date on the profile page
        resp = self.client.get(reverse('view_my_profile'))
        self.assertContains(resp, '123-456-7890')

        self.client.logout()

    def test_register_form_email_incorrect(self):
        form_data = {
            'username': 'an',
            'password1': '1234',
            'mobile_number': '0712341113',
            'email': 'an',
            'alias': '',
            'gender': '',
            'year_of_birth': '1989',
            'identity' : '',
            'tos': True
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_register_form_email_correct(self):
        form_data = {
            'username': 'an@email.com',
            'password1': '1234',
            'mobile_number': '071-234-1113',
            'email': 'an@email.com',
            'alias': '',
            'gender': '',
            'year_of_birth': '1989',
            'identity' : '',
            'tos': True
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_register_form_mobile_number_incorrect(self):
        form_data = {
            'username': 'an@email.com',
            'password1': '1234',
            'mobile_number': '271-234-11132',
            'email': 'an@email.com',
            'alias': '',
            'gender': '',
            'year_of_birth': '1989',
            'identity' : '',
            'tos': True
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_register_form_mobile_number_correct(self):
        form_data = {
            'username': 'an@email.com',
            'password1': '1234',
            'mobile_number': '1-712-341-1134',
            'email': 'an@email.com',
            'alias': '',
            'gender': '',
            'year_of_birth': '1989',
            'identity' : '',
            'tos': True
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_register_form_mobile_number_missing(self):
        form_data = {
            'username': 'an@email.com',
            'password1': '1234',
            'mobile_number': '',
            'email': 'an@email.com',
            'alias': '',
            'gender': '',
            'year_of_birth': '1989',
            'identity': '',
            'tos': True
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_register_form_year_of_birth_incorrect(self):
        form_data = {
            'username': 'an@email.com',
            'password1': '1234',
            'mobile_number': '1-712-341-1134',
            'email': 'an@email.com',
            'alias': '',
            'gender': '',
            'year_of_birth': '2989',
            'identity' : '',
            'tos': True
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    #This testcase used for when user did not edit the email field on the page.
    def test_edit_profile(self):
        edit_profile_form = {
            'username': 'gggdf@ggg.com',
            'first_name': 'testsdgsdg',
            'last_name': 'sgfsdgdgdg',
            'engage_anonymously': True,
            'gender': 'female',
            'alias': 'sdgsdgsdgdg',
            'year_of_birth': 1989,
            'avatar': None,
            'mobile_number': '876-756-4444',
            'email': 'gggdf@ggg.com',
            'identity': ''
        }
        form = EditProfileForm(data=edit_profile_form)
        self.assertEqual(form.is_valid(), True)

    def test_edit_profile_mobile_number_missing(self):
        edit_profile_form = {
            'username': 'gggdf@ggg.com',
            'first_name': 'testsdgsdg',
            'last_name': 'sgfsdgdgdg',
            'engage_anonymously': True,
            'gender': 'female',
            'alias': 'sdgsdgsdgdg',
            'year_of_birth': 1989,
            'avatar': None,
            'mobile_number': '',
            'email': 'gggdf@ggg.com',
            'identity': ''
        }
        form = EditProfileForm(data=edit_profile_form)
        self.assertEqual(form.is_valid(), True)

    # This testcase used for find out the email already exists or not.
    def test_edit_profile_email_already_exist(self):
        # This beloe email address has already been set to user in setup() call.
        edit_profile_form = {
            'username': 'test@email.com', # New edited email address
            'first_name': 'testsdgsdg',
            'last_name': 'sgfsdgdgdg',
            'engage_anonymously': True,
            'gender': 'female',
            'alias': 'sdgsdgsdgdg',
            'year_of_birth': 1989,
            'avatar': None,
            'mobile_number': '876-756-4444',
            'email': 'gggdf@ggg.com', # Current user email address
            'identity': ''
        }
        form = EditProfileForm(data=edit_profile_form)
        self.assertEqual(form.is_valid(), False)

    def test_edit_profile_email_missing(self):
        edit_profile_form = {
            'first_name': 'testsdgsdg',
            'last_name': 'sgfsdgdgdg',
            'engage_anonymously': True,
            'gender': 'female',
            'alias': 'sdgsdgsdgdg',
            'year_of_birth': 1989,
            'avatar': None,
            'mobile_number': '876-756-4444',
            'email': 'gggdf@ggg.com',
            'identity': ''
        }
        form = EditProfileForm(data=edit_profile_form)
        self.assertEqual(form.is_valid(), False)


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


class TestReadOnlyMiddleware(TestCase):

    def setUp(self):
        Site.objects.create(id=2, name='french', domain='fr.site.com')
        self.mw = ReadOnlyMiddleware()

    @override_settings(READ_ONLY_MODE=True)
    def test_process_read_requests(self):
        request_factory = RequestFactory()
        for method in [request_factory.get, request_factory.head]:
            request = method('/path', data={'name': u'test'})
            self.assertEqual(self.mw.process_request(request), None)

    @override_settings(READ_ONLY_MODE=True)
    def test_process_write_request(self):
        request_factory = RequestFactory()
        for method in [request_factory.post, request_factory.put,
                       request_factory.delete, request_factory.options]:
            request = method('/path', data={'name': u'test'})
            response = self.mw.process_request(request)
            self.assertEqual(response.status_code, 405)
            self.assertEqual(response['Allow'], 'HEAD, GET')

    @override_settings(READ_ONLY_MODE=False)
    def test_process_request_read_only_disabled(self):
        request_factory = RequestFactory()
        for method in [request_factory.post, request_factory.put,
                       request_factory.delete, request_factory.options,
                       request_factory.get, request_factory.head]:
            request = method('/path', data={'name': u'test'})
            self.assertEqual(self.mw.process_request(request), None)


class TestReadOnlyContextProcessor(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/path')

    @override_settings(READ_ONLY_MODE=True)
    def test_read_only_mode_enabled(self):
        self.assertEqual(read_only_mode(self.request), {
            'READ_ONLY_MODE': True
        })

    @override_settings(READ_ONLY_MODE=False)
    def test_read_only_mode_disabled(self):
        self.assertEqual(read_only_mode(self.request), {
            'READ_ONLY_MODE': False
        })


class GeneralPrefrencesTestCase(TestCase):

    def setUp(self):
        Site.objects.create(id=2, name='french', domain='fr.site.com')

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

        self.assertFalse(
            preferences.SitePreferences.comments_open(time(5, 0, 0)))
        self.assertFalse(
            preferences.SitePreferences.comments_open(time(23, 30, 0)))
        self.assertTrue(
            preferences.SitePreferences.comments_open(time(11, 0, 0)))
        self.assertTrue(
            preferences.SitePreferences.comments_open(time(21, 59, 59)))

    def test_commenting_times_evening_to_morning(self):
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)

        pref.commenting_time_on = time(22, 0, 0)
        pref.commenting_time_off = time(9, 0, 0)
        pref.save()

        self.assertFalse(
            preferences.SitePreferences.comments_open(time(10, 0, 0)))
        self.assertFalse(
            preferences.SitePreferences.comments_open(time(20, 30, 0)))
        self.assertTrue(
            preferences.SitePreferences.comments_open(time(22, 30, 0)))
        self.assertTrue(
            preferences.SitePreferences.comments_open(time(8, 59, 59)))

    def test_banned_words(self):
        article_url = reverse(
            'category_object_detail',
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

    def test_twitter_meta_tags(self):
        self.post.subtitle = 'the subtitle'
        self.post.save()
        article_url = reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})
        client = Client()
        response = client.get(article_url)

        self.assertContains(
            response,
            '<meta name="twitter:card" content="summary_large_image" />')
        self.assertContains(
            response,
            '<meta name="twitter:title" content="Test">')
        self.assertContains(
            response,
            '<meta name="twitter:description" content="the subtitle">')

    def test_facebook_meta_tags(self):
        self.post.subtitle = 'the subtitle'
        self.post.save()
        article_url = reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})
        client = Client()
        response = client.get(article_url)

        self.assertContains(
            response,
            '<meta property="og:title" content="Test" />')
        self.assertContains(
            response,
            '<meta property="og:url" content="http://testserver/content/detail/test/">')
        self.assertContains(
            response,
            '<meta property="og:description" content="the subtitle" />')

    def test_silenced_words(self):
        article_url = reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_silenced_patterns = 'doodle'
        pref.save()

        params = params_for_comments(self.post, 'sample comment')
        resp = c.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

        params = params_for_comments(self.post, 'some doodle with crap')
        resp = c.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

        resp = c.get(article_url)
        self.assertContains(resp, 'some ****** with crap')

    def test_invalid_banned_words(self):
        article_url = reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_banned_patterns = 'crap\ndoodle\n'  # contains blank line
        pref.save()

        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

    def test_invalid_silenced_words(self):
        article_url = reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_silenced_patterns = 'crap\ndoodle\n'
        pref.save()

        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

    def test_regex_patterns(self):
        article_url = reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.comment_banned_patterns = 'crap\ndoodle\nf**k'
        pref.comment_silenced_patterns = 'monkey'
        pref.save()

        params = params_for_comments(self.post, 'some comment with f**k word')
        resp = c.post(reverse('post_comment'), params)
        self.assertContains(resp, 'inappropriate content')

        params = params_for_comments(
            self.post, 'some comment with CRAP in caps')
        resp = c.post(reverse('post_comment'), params)
        self.assertContains(resp, 'inappropriate content')

        params = params_for_comments(
            self.post, 'word MONKEY which is silenced')
        resp = c.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 302)

        resp = c.get(article_url)

        self.assertContains(resp, 'word ****** which is silenced')


class AfwTestCase(TestCase):

    def test_times(self):

        # Simulate a monday and test true
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(
            0, now=datetime.now() + relativedelta(weekday=MO(-1),
                                                  hour=0, minute=0,
                                                  second=0, microsecond=0))

        self.assertTrue(can_vote)
        self.assertGreater(end_thursday, start_friday)

        # Simulate a wednesday and test false
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(
            0, now=datetime.now() + relativedelta(weekday=WE(-1),
                                                  hour=0, minute=0,
                                                  second=0, microsecond=0))
        self.assertFalse(can_vote)
        self.assertGreater(end_thursday, start_friday)

        # Simulate a monday and test true a week ago
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(
            1, now=datetime.now() + relativedelta(weekday=MO(-1),
                                                  hour=0, minute=0,
                                                  second=0, microsecond=0))

        self.assertTrue(can_vote)
        self.assertGreater(end_thursday, start_friday)

        # Simulate a wednesday and test false a week ago
        can_vote, end_thursday, start_friday = utils.askmama_can_vote(
            1, now=datetime.now() + relativedelta(weekday=WE(-1),
                                                  hour=0, minute=0,
                                                  second=0, microsecond=0))

        self.assertFalse(can_vote)
        self.assertGreater(end_thursday, start_friday)


class CommentingRulesTestCase(TestCase):

    def setUp(self):
        Site.objects.create(id=2, name='french', domain='fr.site.com')

        site = Site.objects.get_current()
        category = Category.objects.create(title='articles', slug='articles')
        self.post = Post.objects.create(title='Test', state='published')
        self.post.primary_category = category
        self.post.sites.add(site)
        self.post.save()
        self.control_user = User.objects.create_user(
            'community_user', 'foo@foo.com', 'foo')
        profile = self.control_user.profile
        profile.accepted_commenting_terms = True
        profile.save()

    def test_comment_views(self):
        # Page detail should show detail page with comment form
        article_url = reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug})

        self.client = Client(HTTP_REFERER='http://localhost%s' % article_url)
        resp = self.client.get(article_url)
        self.assertNotContains(resp, 'Comments are closed.')

        # Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        # Comment should be submitted successfully
        params = params_for_comments(self.post, 'sample comment')
        resp = c.post(reverse('post_comment'), params)
        self.assertEqual(Comment.objects.all().count(), 1)

        # ensure commenting closed
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.commenting_time_on = time(23, 59, 59)
        pref.commenting_time_off = time(0, 0, 1)
        pref.save()

        # clear cache for comments_open context processor
        cache.clear()

        # Comments should be closed
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp, 'Comments are currently closed.')

        # Comment post should fail
        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 400)

        self.assertEqual(Comment.objects.all().count(), 1)

    def test_accept_new_terms(self):
        # Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        # ensure user is prompted to accept terms
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(
            resp,
            'Want to comment? You will need to accept our new '
            'commenting rules first.')

        # agree to terms
        c.post(reverse('agree_comment'))
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))

        # Check agree terms message is gone
        self.assertNotContains(
            resp,
            'Want to comment? You will need to accept our new '
            'commenting rules first.')

    def test_report_user(self):
        # Create and login user
        c = Client()
        c.login(username=self.control_user, password='foo')

        # post unsafe comment
        params = params_for_comments(self.post, 'sample unsafe comment')
        c.post(reverse('post_comment'), params)

        # report user
        c.get(reverse(
            'confirm_comment',
            kwargs={'content_type': 'Post', 'id': 1}))
        resp = c.post(reverse(
            'report_comment',
            kwargs={'content_type': 'Post', 'id': 1, 'vote': -1}))

        # check comment banned
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(
            resp,
            'This comment has been flagged by a community member')
        self.assertTrue(
            BanAudit.objects.filter(banned_by=self.control_user).exists())

    def test_banned_user_comment(self):
        # Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        # check user can comment
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertNotContains(
            resp,
            'Want to comment? You will need to accept our new '
            'commenting rules first.')
        self.assertNotContains(resp, 'Your comment has been flagged')

        # ban user
        utils.ban_user(user, 1, self.control_user)

        # check user cannot comment
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(
            resp,
            'Your comment has been flagged by a community member. '
            'You will not be able to comment again until tomorrow.')
        self.assertTrue(
            BanAudit.objects.filter(banned_by=self.control_user).exists())

    def test_banned_user_comment_by_moderator(self):
        # Create and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        # check user can comment
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertNotContains(
            resp,
            'Want to comment? You will need to accept our new '
            'commenting rules first.')
        self.assertNotContains(resp, 'Your comment has been flagged')

        # ban user
        utils.ban_user(user, 3, self.control_user)

        # check user cannot comment
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(
            resp,
            'Your comment has been reported by a moderator '
            'and you are unable to comment for 3 days')
        self.assertTrue(
            BanAudit.objects.filter(banned_by=self.control_user).exists())

    def test_unban_user(self):
        # Create banned and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.banned = True
        profile.last_banned_date = date.today() - timedelta(days=1)
        profile.ban_duration = 1
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        # check user cannot comment
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp, 'Your comment has been flagged')

        # unban user
        tasks.unban_users()

        # check user can comment
        resp = c.get(reverse(
            'category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertNotContains(resp, 'Your comment has been flagged')

    def test_unban_user_date(self):
        # Create banned and login user
        user = User.objects.create_user('foo', 'foo@foo.com', 'foo')
        profile = UserProfile.objects.create(user=user)
        profile.accepted_commenting_terms = True
        profile.banned = True
        profile.last_banned_date = date.today() - timedelta(days=1)
        profile.ban_duration = 3
        profile.save()
        c = Client()
        c.login(username='foo', password='foo')

        # Test ban unban date is after current date
        unban_date = user.profile.last_banned_date + \
            timedelta(days=user.profile.ban_duration)
        self.assertGreaterEqual(unban_date, date.today())

        # Test unban date is less than 4 days from current date
        self.assertLessEqual(unban_date, date.today() + timedelta(days=4))


class MobileNumberInternationlisationTestCase(TestCase):

    def test_mobile_number_internationalisation(self):
        num = utils.mobile_number_to_international('27123456789')
        self.assertEqual(num, '27123456789')

        num = utils.mobile_number_to_international('0123456789')
        self.assertEqual(num, '27123456789')

class AdminActionsTestCase(TestCase):
    def setUp(self):
        Site.objects.create(id=2, name='french', domain='fr.site.com')
        
    def test_download_users(self):
        adminuser = User.objects.create_superuser('foo', 'foo@foo.com', 'foo')
        adminuser.save()
        fixtures = [User.objects.create_user('bar', 'bar@bar.com', 'bar'),
                    User.objects.create_user('lol', 'lol@lol.com', 'lol')]
        profile1 = UserProfile.objects.create(user=fixtures[0])
        profile2 = UserProfile.objects.create(user=fixtures[1])

        self.client.login(username='foo', password='foo')
        list_url = reverse('admin:auth_user_changelist')
        data = {'action': 'download_csv',
                '_selected_action': [unicode(f.pk) for f in fixtures]}
        response = self.client.post(list_url, data)
        self.assertEqual(response['Content-Type'], "text/csv")
        self.assertContains(response, "bar@bar.com,,,,,")
