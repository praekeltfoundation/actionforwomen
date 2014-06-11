from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from google_credentials import utils
from photon import Client
from django.contrib.auth.models import User
from mama.models import UserProfile

GA_PROFILE_ID = 72027337
init_date = datetime(2013, 8, 26, 0, 0, 0)


class Command(BaseCommand):
    help = 'Pushes various metrics to Holodeck dashboard.'

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

        #Don't use stats older than Vlive launch date
        if datetime_obj < init_date:
            return

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        vlive_users = User.objects.extra(
            where=['last_login - date_joined>%s'],
            params=[timedelta(seconds=60)]
        ).filter(userprofile__origin='vlive')

        print "Pushing Vlive Weekly Users"
        client.send(
            samples=(
                ("Unique Users", vlive_users.filter(
                    date_joined__range=(range_start, range_end)).count()),
                ("Registration", vlive_users.filter(
                    date_joined__range=(range_start, range_end),
                    userprofile__delivery_date__isnull=False).count()),
            ),
            api_key='fb14e8498e564872b05ceda5fc0e5400',
            timestamp=datetime_obj,
        )

        print "Pushing Vlive Weekly Pageviews"
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
            api_key='bf0eabed2a7346bb99b93816c6964ffc',
            timestamp=datetime_obj,
        )

        print "Pushing Vlive User Types"
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
                api_key='f1351ed05c2d4208a843be585928a878',
                timestamp=datetime_obj,
            )

        print "Pushing Mobi User Phase"
        vlive_userprofile = UserProfile.objects.filter(origin='vlive')
        client.send(
            samples=(
                ("Prenatal", vlive_userprofile.filter(
                    delivery_date__gte=datetime_obj).count()),
                ("Postnatal", vlive_userprofile.filter(
                    delivery_date__lt=datetime_obj).count()),
            ),
            api_key='db14a155cb9c49a2b6c2185246b9cf10',
            timestamp=datetime_obj,
        )

    def push_cumulative(self, datetime_obj):
        #Don't use stats older than Vlive launch date
        if datetime_obj < init_date:
            return

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        range_end = datetime_obj
        range_start_cumulative = datetime(2013, 1, 1)
        vlive_users = User.objects.extra(
            where=['last_login - date_joined>%s'],
            params=[timedelta(seconds=60)]
        ).filter(userprofile__origin='vlive')

        print "Pushing Mobi Users Cumulative"
        client.send(
            samples=(
                ("Unique Users", vlive_users.filter(
                    date_joined__lte=range_end).count()),
                ("Registration", vlive_users.filter(
                    date_joined__lte=range_end,
                    userprofile__delivery_date__isnull=False).count()),
            ),
            api_key='1db783e1c9d344e7a39ca685f210633e',
            timestamp=datetime_obj,
        )

        print "Pushing Mobi Pageviews Cumulative"
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
            api_key='1a12d02a71734a1eaacc66f684261d76',
            timestamp=datetime_obj,
        )
