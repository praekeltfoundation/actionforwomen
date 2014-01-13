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

Comment = comments.get_model()

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

    def test_mobi_register(self):
        resp = self.client.get(reverse('registration_register'))
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, 'Are you a..')

        post_data = {
            'username': 'test',
            'password1': '1234',
            'mobile_number': '27123456789',
            'relation_to_baby':'mom_or_mom_to_be',
            'date_qualifier':'due_date',
            'delivery_date_month':0,
            'delivery_date_day':0,
            'delivery_date_year':0
        }

        resp = self.client.post(reverse('registration_register'), post_data)
        self.assertContains(resp, 'Either provide a due date, or check')

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

        #Comment should be submitted successfully
        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(Comment.objects.all().count(), 1)

        #ensure commenting closed
        pref = SitePreferences.objects.get(pk=preferences.SitePreferences.pk)
        pref.commenting_time_on = time(23, 59, 59)
        pref.commenting_time_off = time(0, 0, 1)
        pref.save()

        #clear cache for comments_open context processor
        cache.clear()

        #Comments should be closed
        resp = self.client.get(reverse('category_object_detail',
            kwargs={'category_slug': 'articles', 'slug': self.post.slug}))
        self.assertContains(resp, 'Comments are currently closed.')

        #Comment post should fail
        params = params_for_comments(self.post, 'sample comment')
        resp = self.client.post(reverse('post_comment'), params)
        self.assertEqual(resp.status_code, 400)

        self.assertEqual(Comment.objects.all().count(), 1)

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
