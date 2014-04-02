from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

# This is insane voodoo, but without it the next import Post line does not work.
# TODO: Figure out the insanity when I am less pressed for time.
# Note: This might have to do with the fact that I (Johan) had to:
# pip install -U celery
# to get anything to work on my dev box.
# There is a chance that this could be related to:
# http://stackoverflow.com/questions/3711869/python-import-problem-with-django-management-commands

try:
    from models import Post
except:
    pass


class Command(BaseCommand):
    help = 'Sends out mxit user stage based messages.'

    def handle(self, *args, **options):
        from post.models import Post
        from category.models import Category

        from mama.models import UserProfile
        from mama.tasks import send_mxit_message

        mxit_profiles = UserProfile.objects.filter(origin='mxit')
        total = mxit_profiles.count()
        sent = 0

        for profile in mxit_profiles:
            username = profile.user.username

            # Cannot send message if no due date
            if (profile.date_qualifier in ('unspecified', 'due_date')
                    and profile.delivery_date is None)\
                    or profile.unknown_date:
                print '%s: No due date, so no message' % username
                continue

            delivery_date = profile.delivery_date
            if delivery_date:
                now = datetime.now().date()
                pre_post = 'pre' if profile.is_prenatal() else 'post'
                week = 42 - ((delivery_date - now).days / 7)\
                        if profile.is_prenatal()\
                        else (now - delivery_date).days / 7
            else:
                # Defaults in case user does not have delivery date.
                pre_post = 'pre'
                week = 21

            # Get the category corresponding to the correct week
            try:
                week_category = Category.objects.get(slug="%snatal-week-%s" %
                        (pre_post, week))
            except Category.DoesNotExist:
                print '%s: No category %snatal-week-%s, so no message' %\
                        (username, pre_post, week)
                continue

            # Get the articles for the week category
            object_list = Post.permitted.filter(
                    Q(primary_category=week_category) |
                    Q(categories=week_category)).distinct()

            if not object_list:
                print '%s: No posts for %snatal-week-%s, so no message' %\
                        (username, pre_post, week)
                continue

            msg = ''
            for ob in object_list:
                msg += str(ob.content) + '\n'

            print '%s: %s' % (username, msg)
            send_mxit_message(username, msg)
            sent += 1
        print "%s messages successfully sent of %s possible total" %\
                (sent, total)
        print "Done!"
