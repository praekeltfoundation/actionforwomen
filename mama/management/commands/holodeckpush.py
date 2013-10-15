from datetime import datetime, date, timedelta

from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.core.management.base import BaseCommand
from mama.models import UserProfile
from google_credentials import utils
from photon import Client

GA_PROFILE_ID = 60937138


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
        range_start_cumulative = datetime(year=2012, month=1, day=1, hour=0, minute=0, second=0)

        client = Client(server='http://holodeck.praekelt.com')
        ga_service = utils.get_service()

        mobi_comments = Comment.objects.filter(Q(user__userprofile__origin='mobi')|
                                               Q(user__userprofile__origin__isnull=True))
        vlive_comments = Comment.objects.filter(user__userprofile__origin='vlive')

        mobi_users = User.objects.filter(Q(userprofile__origin='mobi')|
                                         Q(userprofile__origin__isnull=True))

        print "Pushing Weekly Comments"
        client.send(
            samples=(
                ("Mobi", mobi_comments.filter(submit_date__range=(range_start, range_end)).count()),
                ("Vlive", vlive_comments.filter(submit_date__range=(range_start, range_end)).count()),
            ),
            api_key='5bf6a7f19c58454b89ec640bb5799884',
            timestamp=datetime_obj,
        )

        print "Pushing Weekly Comments Cumulative"
        client.send(
            samples=(
                ("Mobi", mobi_comments.filter(submit_date__range=(range_start_cumulative, range_end)).count()),
                ("Vlive", vlive_comments.filter(submit_date__range=(range_start_cumulative, range_end)).count()),
            ),
            api_key='1ee89392a5d74460bfffd991c8a01e0e',
            timestamp=datetime_obj,
        )

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
                ("Registration", mobi_users.filter(date_joined__range=(range_start, range_end)).count()),
            ),
            api_key='2d4946ea24fd451a9a7fc6e950b3b3d3',
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
            api_key='4ca629dd63334526829ecf0ba7dfc253',
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
                api_key='0115a91da7cd4771b8609f3e8fa8ef6f',
                timestamp=datetime_obj,
            )

        print "Pushing Mobi User Phase"
        mobi_userprofile = UserProfile.objects.filter(Q(origin='mobi') |
                                                      Q(origin__isnull=True))
        client.send(
            samples=(
                ("Prenatal", mobi_userprofile.filter(delivery_date__gte=datetime_obj).count()),
                ("Postnatal", mobi_userprofile.filter(delivery_date__lt=datetime_obj).count()),
            ),
            api_key='cd5ad5f4898d4f768e09cf17c9f89b2f',
            timestamp=datetime_obj,
        )

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
                ("Registration", mobi_users.filter(date_joined__range=(range_start_cumulative, range_end)).count()),
            ),
            api_key='4a067ff0cf0844cfa4adda556fd285bb',
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
            api_key='ade53b20f12b4991a6070b9b9108d313',
            timestamp=datetime_obj,
        )
