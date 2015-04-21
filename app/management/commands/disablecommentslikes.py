from django.core.management.base import BaseCommand
from django.db.models import Q
from category.models import Category


class Command(BaseCommand):
    help = 'Disables commenting and liking on authoritative content.'

    def handle(self, *args, **options):
        from post.models import Post
        categories = Category.objects.filter(slug__in=['life-guides', 'mama-a-to-z', 'bc-content'])

        posts = Post.objects.filter(Q(categories__in=categories) | Q(primary_category__in=categories))
        posts.update(
            comments_enabled=False,
            anonymous_comments=False,
            comments_closed=True,
            likes_enabled=False,
            anonymous_likes=False,
            likes_closed=True,
        )
        
        print 'Done! Updated %s posts.' % posts.count()
