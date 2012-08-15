from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.core.management.base import BaseCommand
from photon import Client


class Command(BaseCommand):
    help = 'Pushes various metrics to Holodeck dashboard.'


    def handle(self, *args, **options):
        self.push(datetime.now())
        print "Done!"
                
    def push(self, datetime_obj):
        range_end = datetime_obj
        day_range_start = range_end - timedelta(days=1)
        week_range_start = range_end - timedelta(days=7)
        month_range_start = range_end - timedelta(days=30)

        client = Client(server='http://holodeck.praekelt.com')

        print "Pushing Registrations"
        client.send(
            samples=(
                ("Daily", User.objects.filter(date_joined__range=(day_range_start, range_end)).count()),
                ("Weekly", User.objects.filter(date_joined__range=(week_range_start, range_end)).count()),
                ("Monthly", User.objects.filter(date_joined__range=(month_range_start, range_end)).count()),
            ),
            api_key='f19b87d3cd474faf918d58b71abd4311',
            timestamp=datetime_obj,
        )
        
        print "Pushing Comments"
        client.send(
            samples=(
                ("Daily", Comment.objects.filter(submit_date__range=(day_range_start, range_end)).count()),
                ("Weekly", Comment.objects.filter(submit_date__range=(week_range_start, range_end)).count()),
                ("Monthly", Comment.objects.filter(submit_date__range=(month_range_start, range_end)).count()),
            ),
            api_key='14db95a47181416c9a687976e30f2a6c',
            timestamp=datetime_obj,
        )
