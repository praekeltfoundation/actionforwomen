from haystack.indexes import CharField, SearchIndex, MultiValueField
from haystack import site
from post.models import Post
from django.db.models import Q
from itertools import chain


class PostIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        return Post.permitted.all()

site.register(Post, PostIndex)
