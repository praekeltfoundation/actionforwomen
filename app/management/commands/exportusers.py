import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Exports all users inot users.csv ordered by date joined.'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('-date_joined')

        objects = [dict(user.__dict__.items() +
                   user.profile.__dict__.items()) for user in users]

        csv_writer = csv.writer(
            open('users.csv', 'wb'),
            delimiter=',',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(objects[0].keys())
        for object in objects:
            csv_writer.writerow(object.values())

        print "Done!"
