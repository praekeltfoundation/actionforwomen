from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.core.management.base import BaseCommand
from photon import Client


class Command(BaseCommand):
    help = 'Pushes various metrics to Holodeck dashboard.'

    def handle(self, *args, **options):
   
        range_start = datetime.now()
        range_end = range_start - timedelta(days=1)

        client = Client(server='http://holodeck.praekelt.com')

        print "Pushing Registrations"
        client.send(
            samples=(("Registrations", User.objects.filter(date_joined__range=(range_start, range_end)).count()),),
            api_key='6a01d31eccef43d4bc922104ca3b752d',
            timestamp=datetime.now(),
        )
        
        print "Pushing Comments"
        client.send(
            samples=(("Comments", Comment.objects.filter(submit_date__range=(range_start, range_end)).count()),),
            api_key='0c4912946bb14b8190f800ea6ac8a699',
            timestamp=datetime.now(),
        )
        print "Done!"
