from datetime import datetime, timedelta
import re
import subprocess

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from google_credentials import utils
from photon import Client

GA_PROFILE_ID = 60937138


class Command(BaseCommand):
    help = 'Pushes various metrics to Holodeck dashboard.'


    def handle(self, *args, **options):
        self.push(datetime.now())
        print "Done!"

    def push(self, datetime_obj):
        range_end = datetime_obj
        range_start = range_end - timedelta(days=1)

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        # Get uniques from GA
        print "Fetching uniques from GA"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            segment='gaid::-11', # mobile users only
            metrics='ga:visitors'
        )
        unique_users = query.execute()['totalsForAllResults']['ga:visitors']

        # Get pageviews from GA
        print "Fetching pageviews from GA"
        query = ga_service.data().ga().get(
            ids='ga:%d' % GA_PROFILE_ID,
            start_date=str(range_start.date()),
            end_date=str(range_end.date()),
            segment='gaid::-11', # mobile users only
            metrics='ga:pageviews'
        )
        pageviews = query.execute()['totalsForAllResults']['ga:pageviews']

        # Get mean response time
        print "Determining mean response time."

        p = subprocess.Popen(["ab", "-c", "10", "-n", "10", "http://askapp.mobi/"], stdout=subprocess.PIPE)
        out, err = p.communicate()
        mean_response_time =  re.findall('Total:.*?\d+.*?(\d+)', out)[0]

        client.send(
            samples=(
                ("Pageviews", pageviews),
                ("Unique Users", unique_users),
                ("New Registrations", User.objects.filter(date_joined__range=(range_start, range_end)).count()),
                ("Response Time(ms)", mean_response_time),
            ),
            api_key='6378ed3021ea4073a26b4d00e26c75c6',
            timestamp=datetime_obj,
        )
