from post.models import Post
from datetime import timedelta

i = 0
for post in Post.objects.filter(categories__slug='bc-content'):
    i += 1
    post.created = post.created + timedelta(minutes=i)
    post.save()
    print post
