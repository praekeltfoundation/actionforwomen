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
