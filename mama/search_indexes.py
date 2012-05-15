from haystack import indexes
from post.models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def index_queryset(self):
        return Post.permitted.all()
