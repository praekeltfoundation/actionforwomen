from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from google_credentials import utils
from photon import Client
from django.contrib.auth.models import User
from mama.models import UserProfile

GA_PROFILE_ID = 81239767
init_date = datetime(2014, 2, 1, 0, 0, 0)


class Command(BaseCommand):
    help = 'Pushes various metrics for Mxit to Holodeck dashboard.'

    def handle(self, *args, **options):
        #for i in range (0,20):
        #    self.push(datetime.now() - timedelta(days=i*7))
        #    self.push_cumulative(datetime.now() - timedelta(days=i*7))

        self.push(datetime.now())
        self.push_cumulative(datetime.now())
        print "Done!"

    def push(self, datetime_obj):
        range_end = datetime_obj
        range_start = range_end - timedelta(days=7)

        #Don't use stats older than Mxit launch date
        if datetime_obj < init_date:
            return

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        mxit_users = User.objects.filter(userprofile__origin='mxit')

        print "Pushing Mxit Weekly Users"
        client.send(
            samples=(
                ("Unique Users", mxit_users.filter(
                    date_joined__range=(range_start, range_end)).count()),
                ("Registration", mxit_users.filter(
                    date_joined__range=(range_start, range_end),
                    userprofile__delivery_date__isnull=False).count()),
            ),
            api_key='0ed63f7d41b247cea1353708a3a56c48',
            timestamp=datetime_obj,
        )

        print "Pushing Mxit Weekly Pageviews"
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
            api_key='dd75794cc25548b280d45ad8f6f8455c',
            timestamp=datetime_obj,
        )

        print "Pushing Mxit User Types"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            metrics='ga:visitors',
            dimensions='ga:visitorType',
            segment='gaid::-11',  # mobile users only
        )

        results = query.execute()
        if 'rows' in results:
            client.send(
                samples=[(row[0], int(row[1])) for row in results['rows']],
                api_key='42a1d1d2bfb5451f9f5868dda014e66c',
                timestamp=datetime_obj,
            )

        print "Pushing Mxit User Phase"
        mxit_userprofile = UserProfile.objects.filter(origin='mxit')
        client.send(
            samples=(
                ("Prenatal", mxit_userprofile.filter(
                    delivery_date__gte=datetime_obj).count()),
                ("Postnatal", mxit_userprofile.filter(
                    delivery_date__lt=datetime_obj).count()),
            ),
            api_key='ec0411c2bb7e4374bfd64fb4d430ce08',
            timestamp=datetime_obj,
        )

    def push_cumulative(self, datetime_obj):
        #Don't use stats older than Mxit launch date
        if datetime_obj < init_date:
            return

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        range_end = datetime_obj
        range_start_cumulative = datetime(2013, 1, 1)
        mxit_users = User.objects.filter(userprofile__origin='mxit')

        print "Pushing Mxit Users Cumulative"
        client.send(
            samples=(
                ("Unique Users", mxit_users.filter(
                    date_joined__lte=range_end).count()),
                ("Registration", mxit_users.filter(
                    date_joined__lte=range_end,
                    userprofile__delivery_date__isnull=False).count()),
            ),
            api_key='aba5dc3365b74c118e89132e73c15cb7',
            timestamp=datetime_obj,
        )

        print "Pushing Mxit Pageviews Cumulative"
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
            api_key='f465c0825d0647a88d5a6ca6ebdb8f93',
            timestamp=datetime_obj,
        )
