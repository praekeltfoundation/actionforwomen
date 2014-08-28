from haystack.indexes import CharField, SearchIndex
from haystack import site
from post.models import Post
from mama.models import Comment
from livechat.models import LiveChat


class PostIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        return Post.permitted.all()

site.register(Post, PostIndex)


class CommentIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        ask_mama = Post.objects.get(primary_category__slug='ask-mama')
        return Comment.objects.filter(
            object_pk=ask_mama.id,
            replied_to_comments_set__isnull=False,
            ).distinct()

site.register(Comment, CommentIndex)
