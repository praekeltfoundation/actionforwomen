from django.core.management.base import BaseCommand
from jmbo.models import ModelBase


class Command(BaseCommand):
    help = 'Imports raw Baby Center baby content.'

    def handle(self, *args, **options):
        print 'Migrate Jmbo Models to Zambia'
        self.chunked_migrate(ModelBase)

    def chunked_migrate(self, model):
        i = 0
        chunk = 100
        while True:
            qs = model.objects.exclude(sites=2)[:chunk]
            if not qs.exists():
                print 'Nothing to migrate.'
                break
            for p in qs:
                p.sites.add(2)
            i += chunk
            print 'Items migrated to Zambia: ', i
