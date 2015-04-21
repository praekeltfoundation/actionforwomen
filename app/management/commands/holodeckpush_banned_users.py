from datetime import datetime

from django.core.management.base import BaseCommand
from photon import Client


class Command(BaseCommand):
    help = 'Pushes banned user metrics to Holodeck dashboard.'

    def handle(self, *args, **options):
        self.push_banned_users()
        print "Done!"

    def push_banned_users(self):
        from mama.models import UserProfile
        client = Client(server='http://holodeck.praekelt.com')
        ban_1 = UserProfile.objects.filter(banned=True, ban_duration=1).count()
        ban_3 = UserProfile.objects.filter(banned=True, ban_duration=3).count()
        banned = UserProfile.objects.filter(banned=True).count()

        client.send(
            samples=(
                ("Community Ban", ban_1),
                ("Moderator Ban", ban_3),
                ("Total", banned),
            ),
            api_key='43d20f761ec14355afc252ed9d7cb995',
            timestamp=datetime.now(),
        )
