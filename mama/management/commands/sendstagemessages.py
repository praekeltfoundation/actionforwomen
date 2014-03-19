from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from mama.models import UserProfile
from mama.utils import send_message
from django.db.models import Q
from category.models import Category
from post.models import Post


class Command(BaseCommand):
    help = 'Sends out mxit user stage based messages.'

    def handle(self, *args, **options):
        mxit_profiles = UserProfile.objects.filter(origin='mxit')
        for profile in mxit_profiles:
            username = profile.user.username

            # Cannot send message if no due date
            if (profile.date_qualifier in (
                    'unspecified', 'due_date'
                    ) and profile.delivery_date is None) or profile.unknown_date:
                print '%s: No due date, so no message' % username
                continue

            delivery_date = profile.delivery_date
            if delivery_date:
                now = datetime.now().date()
                pre_post = 'pre' if profile.is_prenatal() else 'post'
                week = 42 - ((delivery_date - now).days / 7) if profile.is_prenatal() else (now - delivery_date).days / 7
            else:
                # Defaults in case user does not have delivery date.
                pre_post = 'pre'
                week = 21

            # Get the category corresponding to the correct week
            try:
                week_category = Category.objects.get(slug="%snatal-week-%s" % (pre_post, week))
            except Category.DoesNotExist:
                print '%s: No category %snatal-week-%s, so no message' % (username, pre_post, week)
                continue

            # Get the articles for the week category
            object_list = Post.permitted.filter(Q(primary_category=week_category) |
                                                Q(categories=week_category)).distinct()

            if not object_list:
                print '%s: No posts for %snatal-week-%s, so no message' % (username, pre_post, week)
                continue

            msg = ''
            for ob in object_list:
                msg += str(ob.content)

            print '%s: %s' % (username, msg)
            try:
                send_message(settings.MXIT_CLIENT_ID,
                             settings.MXIT_CLIENT_SECRET,
                             "http://juizi.dyndns.org:8000/",
                             settings.MXIT_APP_ID,
                             [username],
                             msg)
                print 'Success!'
            except Exception as e:
                print 'Could not send:'
                print e
        print "Done!"
