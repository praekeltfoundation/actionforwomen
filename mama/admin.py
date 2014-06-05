from datetime import datetime
from dateutil.relativedelta import *

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.comments.models import Comment
from django.contrib.admin.sites import NotRegistered
from django.contrib.contenttypes.models import ContentType
from jmbo.models import ModelBase,Relation
from jmbo.admin import ModelBaseAdmin
from preferences.admin import PreferencesAdmin
from moderator.admin import (
    CommentAdmin, AdminModeratorMixin, HamCommentAdmin, ReportedCommentAdmin,
    SpamCommentAdmin, UnsureCommentAdmin)
from moderator.models import (
    HamComment, ReportedComment, SpamComment, UnsureComment)

from secretballot.models import Vote
from post.models import Post
from poll.models import Poll
from poll.admin import PollAdmin
from jmboyourwords.admin import YourStoryEntryAdmin
from jmboyourwords.models import YourStoryEntry
from livechat.models import LiveChat
from livechat.admin import LiveChatAdmin

from category.models import Category
from survey.models import ContentQuizToPost
from mama.models import (
    Link,
    NavigationLink,
    SitePreferences,
    Banner,
    DefaultAvatar,
    ArticlePost,
    MomsStoryPost
)


class MamaModelbaseAdmin(AdminModeratorMixin, ModelBaseAdmin):
    raw_id_fields = ('owner', )


class LinkInline(admin.TabularInline):
    model = Link
    fk_name = 'source'
    extra = 1
    raw_id_fields = ('target', )


class NavigationLinkInline(admin.TabularInline):
    model = NavigationLink
    fk_name = 'source'


class ContentQuizInline(admin.TabularInline):
    model = ContentQuizToPost
    fk_name = 'post'


class PostAdmin(MamaModelbaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        LinkInline,
        NavigationLinkInline,
        ContentQuizInline
    ]
    list_display = (
        'title', 'primary_category', 'publish_on', 'retract_on',
        '_get_absolute_url', 'is_featured', 'created', '_actions'
    )
    ordering = ('-publish_on', '-created')

    def is_featured(self, obj, *args, **kwargs):
        return obj.categories.filter(slug='featured').exists()
    is_featured.boolean = True


class MamaPostAdmin(PostAdmin):
    def queryset(self, request):
        qs = super(MamaPostAdmin, self).queryset(request)
        return qs.filter(
            primary_category__slug=self.model.primary_category_slug)


class MamaPollAdmin(PollAdmin):
    raw_id_fields = ('owner', )


class BannerAdmin(MamaModelbaseAdmin):
    list_filter = (
        'state',
        'created',
        'sites',
        'banner_type'
    )
    list_display = (
        'title', 'description', 'thumbnail', 'schedule', '_actions',
        'publish_on', 'retract_on', 'created')

    def thumbnail(self, obj, *args, **kwargs):
        return '<img src="%s" />' % (obj.image.url,)
    thumbnail.allow_tags = True

    def schedule(self, obj, *args, **kwargs):
        if(obj.time_on and obj.time_off):
            return 'Randomly selected by Vlive between %s and %s' % (
                obj.time_on, obj.time_off)
        return 'Randomly selected by Vlive'


class DefaultAvatarAdmin(admin.ModelAdmin):
    list_display = ('_image',)

    def _image(self, obj):
        # todo: use correct photologue scale
        if obj.image:
            return '<img src="%s" height="48" width="48" />' % obj.image.url
        return ""
    _image.short_description = 'Image'
    _image.allow_tags = True


class MamaYourStoryEntryAdmin(YourStoryEntryAdmin):
    list_display = ('name', 'user', 'user_msisdn', 'text', 'created',)

    def user_msisdn(self, obj):
        # return the msisdn of the user
        profile = obj.user.profile
        return profile.mobile_number


class AskMamaQuestion(Comment):
    class Meta:
        proxy = True
        verbose_name = "Question for MAMA"
        verbose_name_plural = "Questions for MAMA"
        ordering = None


class WeeklyFilter(admin.filters.SimpleListFilter):
    """
    Filter to allow filtering the mama questions by this week, last week, etc.
    """
    title = 'Week'
    parameter_name = 'weeks_ago'

    def lookups(self, request, model_admin):
        return (
            ('0', _('this week')),
            ('1', _('last week')),
            ('2', _('older')),
        )

    def queryset(self, request, queryset):
        # see if there is a filter value in place, to apply
        try:
            weeks_ago = int(self.value())
        except TypeError:
            # there is no filter value
            # default to showing this weeks
            weeks_ago = 0

        # Find the dates for the current week, starting last Friday and ending
        # next Thursday
        NOW = datetime.now()
        start_friday = NOW + relativedelta(weekday=FR(-1),
                                           hour=0, minute=0,
                                           second=0, microsecond=0)
        end_thursday = NOW + relativedelta(weekday=TH(+1),
                                           hour=0, minute=0,
                                           second=0, microsecond=0,
                                           microseconds=-1)
        if end_thursday < start_friday:
            end_thursday += relativedelta(weeks=1)

        # Subtract the amount of weeks in the past.
        if weeks_ago > 0:
            start_friday = start_friday + relativedelta(weeks=-weeks_ago)
            end_thursday = end_thursday + relativedelta(weeks=-weeks_ago)

        if weeks_ago < 2:
            # Filter the questions between the date range
            queryset = queryset.filter(submit_date__range=(start_friday,
                                                           end_thursday,))
        else:
            # Filter all the older questions.
            queryset = queryset.filter(submit_date__lt=(end_thursday))

        return queryset


class AskMamaQuestionAdmin(CommentAdmin):
    """ Add a filter to filter out 'This week's favourite stories' in CMS
    """
    list_display = ('comment_text', 'user', 'vote_score', 'submit_date',
                    'moderator_reply', 'is_removed')
    list_filter = (WeeklyFilter, 'is_removed',)
    date_hierarchy = None
    ordering = None

    def vote_score(self, obj):
        return obj.vote_score
    vote_score.admin_order_field = 'vote_score'

    def queryset(self, request):
        """ Filter the questions that have been submitted this week in the
            AskMama section.
        """
        latest_pinned = self.get_askmama_latest_pinned_post()
        if latest_pinned:
            pct = ContentType.objects.get_for_model(latest_pinned.__class__)

            # Filter the comments linked to the post
            questions = AskMamaQuestion.objects.filter(
                content_type=pct,
                object_pk=latest_pinned.id)
        else:
            questions = AskMamaQuestion.objects.none()

        # leave out the moderator answers
        questions = questions.exclude(user__is_staff=True)

        # Work out the vote count for the questions, to sort by the most liked
        # questions, i.e. questions with the most votes. (This is taken from
        # the  MostLikedItem view modifier item in jmbo)
        questions = questions.extra(
            select={
                'vote_score': '(SELECT COUNT(*) from %s WHERE vote=1 AND \
    object_id=%s.%s AND content_type_id=%s) - (SELECT COUNT(*) from %s WHERE \
    vote=-1 AND object_id=%s.%s AND content_type_id=%s)' % (
                Vote._meta.db_table,
                Comment._meta.db_table,
                Comment._meta.pk.attname,
                ContentType.objects.get_for_model(Comment).id,
                Vote._meta.db_table,
                Comment._meta.db_table,
                Comment._meta.pk.attname,
                ContentType.objects.get_for_model(Comment).id)
            }
        )
        questions = questions.order_by('-vote_score', '-submit_date')

        return questions

    def get_askmama_latest_pinned_post(self):
        """ Get the latest askmama category pinned post
        """
        try:
            category = Category.objects.get(slug__iexact='ask-mama')
        except Category.DoesNotExist:
            return None
        try:
            return Post.permitted.filter(
                pin__category=category
            ).latest('created')
        except Post.DoesNotExist:
            return None


class HiddenModelAdmin(admin.ModelAdmin):
    """
    As of writing Django has difficulty associating admin permissions to
    Proxy models (see 11154). This class can be used to soft-hide(popup adds
    etc will still work) models on admin home via code instead of relying on
    admin permissions.
    """
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


class AskMamaPreferencesAdmin(PreferencesAdmin):
    raw_id_fields = ('contact_email_recipients', )


class MamaLiveChatAdmin(AdminModeratorMixin, LiveChatAdmin):
    pass


class MamaCommentAdmin(CommentAdmin):
    def get_user_display_name(self, obj):
        if obj.name.lower().startswith('anon'):
            return obj.user.username
        return obj.name


class MamaHamCommentAdmin(MamaCommentAdmin, HamCommentAdmin):
    pass


class MamaReportedCommentAdmin(MamaCommentAdmin, ReportedCommentAdmin):
    pass


class MamaSpamCommentAdmin(MamaCommentAdmin, SpamCommentAdmin):
    pass


class MamaUnsureCommentAdmin(MamaCommentAdmin, UnsureCommentAdmin):
    pass


admin.site.register(SitePreferences, AskMamaPreferencesAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(DefaultAvatar, DefaultAvatarAdmin)
admin.site.register(ModelBase, HiddenModelAdmin)
try:
    admin.site.unregister(Post)
    admin.site.unregister(Poll)
except NotRegistered:
    pass
admin.site.register(Post, PostAdmin)
admin.site.register(ArticlePost, MamaPostAdmin)
admin.site.register(MomsStoryPost, MamaPostAdmin)
admin.site.register(Poll, MamaPollAdmin)

admin.site.unregister(Comment)
admin.site.unregister(HamComment)
admin.site.unregister(ReportedComment)
admin.site.unregister(SpamComment)
admin.site.unregister(UnsureComment)
admin.site.register(Comment, MamaCommentAdmin)
admin.site.register(HamComment, MamaHamCommentAdmin)
admin.site.register(ReportedComment, MamaReportedCommentAdmin)
admin.site.register(SpamComment, MamaSpamCommentAdmin)
admin.site.register(UnsureComment, MamaUnsureCommentAdmin)

try:
    admin.site.unregister(YourStoryEntry)
    admin.site.unregister(LiveChat)
except NotRegistered:
    pass
admin.site.register(YourStoryEntry, MamaYourStoryEntryAdmin)
admin.site.register(LiveChat, MamaLiveChatAdmin)

admin.site.register(AskMamaQuestion, AskMamaQuestionAdmin)

admin.site.unregister(Relation)
admin.site.register(Relation, HiddenModelAdmin)

