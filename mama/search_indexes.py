from haystack.indexes import CharField, SearchIndex
from haystack import site
from post.models import Post


class PostIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        return Post.permitted.all()

site.register(Post, PostIndex)
