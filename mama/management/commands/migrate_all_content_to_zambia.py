from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports raw Baby Center baby content.'

    def handle(self, *args, **options):
        from jmbo.models import ModelBase
        from poll.models import Poll

        print 'Migrate Jmbo Models to Zambia'
        self.chunked_migrate(ModelBase)

        print 'Un migrate Poll for Zambia'
        self.chunked_un_migrate(Poll)

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

    def chunked_un_migrate(self, model):
        i = 0
        chunk = 100
        while True:
            qs = model.objects.filter(sites=2)[:chunk]
            if not qs.exists():
                print 'Nothing to un-migrate.'
                break
            for p in qs:
                p.sites = [1, ]
                p.save()
            i += chunk
            print 'Items un-migrated to Zambia: ', i
