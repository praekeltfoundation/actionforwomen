from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports raw Baby Center content (both pregancy and baby).'

    def handle(self, *args, **options):
        call_command('importbcpregnancycontent')
        call_command('importbcbabycontent')
