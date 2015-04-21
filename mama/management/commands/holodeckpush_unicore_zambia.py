from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from google_credentials import utils
from photon import Client
from mama.models import UserProfile

GA_PROFILE_ID = 88472004
init_date = datetime(2014, 7, 14)
PROFILE_ORIGIN = 'unicore_zambia'

HOLODECK_API_KEYS = {
    'users_weekly': '78f2376077544db4878e409c0b07adda',
    'pageviews_weekly': '0a12d44a7f394e76b301461c3e77f9c4',
    'user_types': 'a537416aa8064fe29c6495c474fb4b44',
    'user_phase': '3e8d0fd9f8924379b9c6bfac9e58045f',
    'users_cumulative': '58d0998073d74c7495bc8233fe7380cb',
    'pageviews_cumulative': '6909a9c8c2974c69b0c929c258d02688',
    'comments_weekly': 'cebc703a64eb4e88ae468f6ee4db77dc',
    'comments_cumulative': '00ada2b9166e43afb27149dd89ce493d'
}


class Command(BaseCommand):
    help = 'Pushes various metrics for Zambia Unicore to Holodeck dashboard.'

    def handle(self, *args, **options):
        self.push(datetime.now())
        self.push_cumulative(datetime.now())
        print "Done!"

    def push(self, datetime_obj):
        range_end = datetime_obj
        range_start = range_end - timedelta(days=7)

        # Don't use stats older than Unicore launch date
        if datetime_obj < init_date:
            return

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        unicore_users = User.objects.filter(userprofile__origin=PROFILE_ORIGIN)

        print "Pushing Zambia Weekly Users"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            segment='gaid::-11',  # mobile users only
            metrics='ga:users'
        )

        results = query.execute()
        client.send(
            samples=(
                ("GA Users", results['totalsForAllResults']['ga:users']),
                ("Registration", unicore_users.filter(
                    date_joined__range=(range_start, range_end)).count()),
            ),
            api_key=HOLODECK_API_KEYS['users_weekly'],
            timestamp=datetime_obj,
        )

        print "Pushing Zambia Weekly Pageviews"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            segment='gaid::-11',  # mobile users only
            metrics='ga:pageviews'
        )

        results = query.execute()
        client.send(
            samples=(
                ("Pageviews", results['totalsForAllResults']['ga:pageviews']),
            ),
            api_key=HOLODECK_API_KEYS['pageviews_weekly'],
            timestamp=datetime_obj,
        )

        print "Pushing Zambia User Types"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            metrics='ga:users',
            dimensions='ga:userType',
            segment='gaid::-11',  # mobile users only
        )

        results = query.execute()
        if 'rows' in results:
            client.send(
                samples=[(row[0], int(row[1])) for row in results['rows']],
                api_key=HOLODECK_API_KEYS['user_types'],
                timestamp=datetime_obj,
            )

        print "Pushing Zambia User Phase"
        unicore_userprofile = UserProfile.objects.filter(origin=PROFILE_ORIGIN)
        client.send(
            samples=(
                ("Prenatal", unicore_userprofile.filter(
                    delivery_date__gte=datetime_obj).count()),
                ("Postnatal", unicore_userprofile.filter(
                    delivery_date__lt=datetime_obj).count()),
            ),
            api_key=HOLODECK_API_KEYS['user_phase'],
            timestamp=datetime_obj,
        )

        print "Pushing Zambia Weekly Comments"
        unicore_comments = Comment.objects.filter(
            site=Site.objects.get_current(),
            user__userprofile__origin=PROFILE_ORIGIN)

        client.send(
            samples=(
                ("Mobi", unicore_comments.filter(
                    submit_date__range=(range_start, range_end)).count()),
            ),
            api_key=HOLODECK_API_KEYS['comments_weekly'],
            timestamp=datetime_obj,
        )

    def push_cumulative(self, datetime_obj):
        # Don't use stats older than Unicore launch date
        if datetime_obj < init_date:
            return

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        range_end = datetime_obj
        range_start_cumulative = init_date
        unicore_users = User.objects.filter(userprofile__origin=PROFILE_ORIGIN)

        print "Pushing Zambia Users Cumulative"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start_cumulative.date()),
            end_date=str(range_end.date()),
            metrics='ga:users',
            segment='gaid::-11',  # mobile users only
        )

        results = query.execute()
        client.send(
            samples=(
                ("GA Users", results['totalsForAllResults']['ga:users']),
                ("Registration", unicore_users.filter(
                    date_joined__range=(range_start_cumulative,
                                        range_end)).count()),
            ),
            api_key=HOLODECK_API_KEYS['users_cumulative'],
            timestamp=datetime_obj,
        )

        print "Pushing Zambia Pageviews Cumulative"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start_cumulative.date()),
            end_date=str(range_end.date()),
            metrics='ga:pageviews',
            segment='gaid::-11',  # mobile users only
        )

        results = query.execute()
        client.send(
            samples=(
                ("Pageviews", results['totalsForAllResults']['ga:pageviews']),
            ),
            api_key=HOLODECK_API_KEYS['pageviews_cumulative'],
            timestamp=datetime_obj,
        )

        print "Pushing Zambia Comments Cumulative"
        unicore_comments = Comment.objects.filter(
            user__userprofile__origin=PROFILE_ORIGIN)

        client.send(
            samples=(
                ("Mobi", unicore_comments.filter(
                    submit_date__range=(range_start_cumulative,
                                        range_end)).count()),
            ),
            api_key=HOLODECK_API_KEYS['comments_cumulative'],
            timestamp=datetime_obj,
        )
