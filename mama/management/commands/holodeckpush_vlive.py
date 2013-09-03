from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from google_credentials import utils
from photon import Client

GA_PROFILE_ID = 72027337


class Command(BaseCommand):
    help = 'Pushes various metrics to Holodeck dashboard.'


    def handle(self, *args, **options):
        #for i in range (0,20):
        #    self.push(datetime.now() - timedelta(days=i*7))
        self.push(datetime.now())
        self.push_cumulative(datetime.now())
        print "Done!"

    def push(self, datetime_obj):
        range_end = datetime_obj
        range_start = range_end - timedelta(days=7)

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        print "Pushing Mobi Weekly Users"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            segment='gaid::-11', # mobile users only
            metrics='ga:visitors'
        )

        results = query.execute()
        client.send(
            samples=(
                ("Unique Users", results['totalsForAllResults']['ga:visitors']),
            ),
            api_key='fb14e8498e564872b05ceda5fc0e5400',
            timestamp=datetime_obj,
        )

        print "Pushing Mobi Weekly Pageviews"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            segment='gaid::-11', # mobile users only
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

        print "Pushing Mobi User Types"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            metrics='ga:visitors',
            dimensions='ga:visitorType',
            segment='gaid::-11', # mobile users only
        )

        results = query.execute()
        if 'rows' in results:
            client.send(
                samples=[(row[0], int(row[1])) for row in results['rows']],
                api_key='f1351ed05c2d4208a843be585928a878',
                timestamp=datetime_obj,
            )


    def push_cumulative(self, datetime_obj):
        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        range_end = datetime_obj
        range_start_cumulative = datetime(2013, 8, 27, 0, 0, 0)

        print "Pushing Mobi Users Cumulative"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start_cumulative.date()),
            end_date=str(range_end.date()),
            metrics='ga:visitors',
            segment='gaid::-11', # mobile users only
        )

        results = query.execute()
        client.send(
            samples=(
                ("Unique Users", results['totalsForAllResults']['ga:visitors']),
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
            segment='gaid::-11', # mobile users only
        )

        results = query.execute()
        client.send(
            samples=(
                ("Pageviews", results['totalsForAllResults']['ga:pageviews']),
            ),
            api_key='1a12d02a71734a1eaacc66f684261d76',
            timestamp=datetime_obj,
        )
