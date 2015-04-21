from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Unbans all users based on their banned duration.'

    def handle(self, *args, **options):
        from app.tasks import unban_users
        unban_users()
        print "Done!"
