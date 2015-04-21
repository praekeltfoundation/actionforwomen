from haystack.indexes import CharField, SearchIndex, MultiValueField
from haystack import site
from post.models import Post
from django.contrib.comments import Comment
from moderator.models import CommentReply
from livechat.models import LiveChat, LiveChatResponse
from django.db.models import Q
from itertools import chain


class PostIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        return Post.permitted.all()

site.register(Post, PostIndex)


class CommentIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        ask_mama = Post.objects.get(primary_category__slug='ask-mama')
        livechats = LiveChat.objects.all()
        livechatresponse = LiveChatResponse.objects.all()

        return Comment.objects.filter(Q(
            object_pk__in=[ask_mama.id, ] + [chat.id for chat in livechats],
            replied_to_comments_set__isnull=False) | Q(
            id__in=[comment.comment_id for comment in livechatresponse]))


site.register(Comment, CommentIndex)


class CommentReplyIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        ask_mama = Post.objects.get(primary_category__slug='ask-mama')

        return CommentReply.objects.filter(
            replied_to_comments__object_pk__in=[ask_mama.id,])

site.register(CommentReply, CommentReplyIndex)


class LiveChatResponseIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        return LiveChatResponse.objects.all()

site.register(LiveChatResponse, LiveChatResponseIndex)

