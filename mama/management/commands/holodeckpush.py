from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.core.management.base import BaseCommand
from photon import Client


class Command(BaseCommand):
    help = 'Pushes various metrics to Holodeck dashboard.'

    def handle(self, *args, **options):
   
        range_end = datetime.now()
        day_range_start = range_end - timedelta(days=1)
        week_range_start = range_end - timedelta(days=7)

        client = Client(server='http://holodeck.praekelt.com')

        print "Pushing Registrations"
        client.send(
            samples=(
                ("Daily", User.objects.filter(date_joined__range=(day_range_start, range_end)).count()),
                ("Weekly", User.objects.filter(date_joined__range=(week_range_start, range_end)).count()),
            ),
            api_key='6a01d31eccef43d4bc922104ca3b752d',
            timestamp=datetime.now(),
        )
        
        print "Pushing Comments"
        client.send(
            samples=(
                ("Daily", Comment.objects.filter(submit_date__range=(day_range_start, range_end)).count()),
                ("Weekly", Comment.objects.filter(submit_date__range=(week_range_start, range_end)).count()),
            ),
            api_key='0c4912946bb14b8190f800ea6ac8a699',
            timestamp=datetime.now(),
        )
        print "Done!"
