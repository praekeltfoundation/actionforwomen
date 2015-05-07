import publisher
from publisher import admin

from djcelery import admin
import djcelery

import south_admin
from south_admin import admin

from datetime import datetime
from dateutil.relativedelta import *

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.comments.models import Comment
from django.contrib.admin.sites import NotRegistered
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from jmbo.models import ModelBase, Relation
from jmbo.admin import ModelBaseAdmin
from preferences.admin import PreferencesAdmin
from moderator.admin import (
    CommentAdmin, AdminModeratorMixin, HamCommentAdmin, ReportedCommentAdmin,
    SpamCommentAdmin, UnsureCommentAdmin)
from moderator.models import (
    HamComment, ReportedComment, SpamComment, UnsureComment)
from moderator import utils

from secretballot.models import Vote
from post.models import Post
from poll.models import Poll
from poll.admin import PollAdmin
from jmboyourwords.admin import YourStoryEntryAdmin
from jmboyourwords.models import YourStoryEntry, YourStoryCompetition
from livechat.models import LiveChat, LiveChatResponse
from livechat.admin import LiveChatAdmin

from app.utils import ban_user
from category.models import Category
from survey.models import ContentQuizToPost
from app.models import (
    Link,
    NavigationLink,
    SitePreferences,
    Banner,
    DefaultAvatar,
    SupportPost,
    StoryPost,
    FAQPost,
    BanAudit
)


class ActonforwomenModelbaseAdmin(AdminModeratorMixin, ModelBaseAdmin):
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


class PostAdmin(ActonforwomenModelbaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        LinkInline,
        NavigationLinkInline,
        ContentQuizInline
    ]
    list_display = (
        'title', 'primary_category', 'publish_on', 'retract_on',
        '_get_absolute_url', 'is_featured', 'created', '_actions',
        '_view_comments'
    )
    ordering = ('-publish_on', '-created')
    list_per_page = 10
    readonly_fields = ('created',)

    def queryset(self, request):
        qs = super(PostAdmin, self).queryset(request)
        return qs.distinct()

    def is_featured(self, obj, *args, **kwargs):
        return obj.categories.filter(slug='featured').exists()
    is_featured.boolean = True

    def _view_comments(self, article):
        return '<a href="/admin/post/%s/%s/moderate/">View (%s)</a>' % (
            article._meta.module_name,
            article.pk, article.comment_count)

    _view_comments.short_description = 'Comments'
    _view_comments.allow_tags = True


class ActonforwomenPostAdmin(PostAdmin):

    def queryset(self, request):
        qs = super(ActonforwomenPostAdmin, self).queryset(request)
        return qs.filter(
            primary_category__slug=self.model.primary_category_slug)


class ActonforwomenPollAdmin(PollAdmin):
    raw_id_fields = ('owner', )


class BannerAdmin(ActonforwomenModelbaseAdmin):
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


class ActionforwomenYourStoryEntryAdmin(YourStoryEntryAdmin):
    list_display = ('name', 'user', 'user_msisdn', 'text', 'created',)

    def user_msisdn(self, obj):
        # return the msisdn of the user
        profile = obj.user.profile
        return profile.mobile_number


class Question(Comment):

    class Meta:
        proxy = True
        verbose_name = "Question for expert"
        verbose_name_plural = "Questions for expert"
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


class QuestionAdmin(CommentAdmin):

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
            question section.
        """
        latest_pinned = self.get_askmama_latest_pinned_post()
        if latest_pinned:
            pct = ContentType.objects.get_for_model(latest_pinned.__class__)

            # Filter the comments linked to the post
            questions = Question.objects.filter(
                content_type=pct,
                object_pk=latest_pinned.id)
        else:
            questions = Question.objects.none()

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
            category = Category.objects.get(slug__iexact='question')
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


class ActionforwomenPreferencesAdmin(PreferencesAdmin):
    raw_id_fields = ('contact_email_recipients', )


class ActionforwomenLiveChatAdmin(AdminModeratorMixin, LiveChatAdmin):
    pass


class ActionforwomenCommentAdmin(CommentAdmin):
    actions = CommentAdmin.actions + ['mark_spam_no_ban', ]

    def get_user_display_name(self, obj):
        if obj.name.lower().startswith('anon'):
            return obj.user.username
        return obj.name

    def mark_spam(self, modeladmin, request, queryset):
        for comment in queryset:
            utils.classify_comment(comment, cls='spam')
            ban_user(comment.user, 3, request.user)

        self.message_user(
            request,
            "%s comment(s) successfully marked as spam. +3 day ban" % queryset.count()
        )
    mark_spam.short_description = "Mark selected comments as spam (3 day ban)"


    def mark_spam_no_ban(self, modeladmin, request, queryset):
        for comment in queryset:
            utils.classify_comment(comment, cls='spam')

        self.message_user(
            request,
            "%s comment(s) successfully marked as spam. (no ban)" % queryset.count()
        )
    mark_spam_no_ban.short_description = "Mark selected comments as spam (no ban)"


class ActionforwomenHamCommentAdmin(
        ActionforwomenCommentAdmin, HamCommentAdmin):
    pass


class ActionforwomenReportedCommentAdmin(
        ActionforwomenCommentAdmin, ReportedCommentAdmin):
    pass


class ActionforwomenSpamCommentAdmin(
        ActionforwomenCommentAdmin, SpamCommentAdmin):
    pass


class ActionforwomenUnsureCommentAdmin(
        ActionforwomenCommentAdmin, UnsureCommentAdmin):
    pass


class ModelBaseHiddenAdmin(ActonforwomenModelbaseAdmin, HiddenModelAdmin):
    pass


class BanAuditAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'banned_by', 'banned_on', 'ban_duration', '_is_banned')
    list_filter = ('banned_on', 'ban_duration')
    raw_id_fields = ('user', 'banned_by')
    readonly_fields = ('user', 'banned_by', 'ban_duration')
    search_fields = ['user__username', 'banned_by__username']
    date_hierarchy = 'banned_on'
    actions = None

    def _is_banned(self, obj, *args, **kwargs):
        return obj.user.profile.banned
    _is_banned.short_description = 'Banned'
    _is_banned.allow_tags = True
    _is_banned.boolean = True

    def has_delete_permission(self, request, obj=None, *args, **kwargs):
        return False


admin.site.register(BanAudit, BanAuditAdmin)
admin.site.register(SitePreferences, ActionforwomenPreferencesAdmin)
admin.site.register(DefaultAvatar, DefaultAvatarAdmin)

admin.site.register(ModelBase, ModelBaseHiddenAdmin)
try:
    admin.site.unregister(Post)
    admin.site.unregister(Poll)
except NotRegistered:
    pass
admin.site.register(Post, PostAdmin)
admin.site.register(StoryPost, ActonforwomenPostAdmin)
admin.site.register(SupportPost, ActonforwomenPostAdmin)
admin.site.register(FAQPost, ActonforwomenPostAdmin)
admin.site.register(Poll, ActonforwomenPollAdmin)

admin.site.unregister(Comment)
admin.site.unregister(HamComment)
admin.site.unregister(ReportedComment)
admin.site.unregister(SpamComment)
admin.site.unregister(UnsureComment)
admin.site.register(Comment, ActionforwomenCommentAdmin)
admin.site.register(HamComment, ActionforwomenHamCommentAdmin)
admin.site.register(ReportedComment, ActionforwomenReportedCommentAdmin)
admin.site.register(SpamComment, ActionforwomenSpamCommentAdmin)
admin.site.register(UnsureComment, ActionforwomenUnsureCommentAdmin)

from userprofile.admin import ProfileInline

try:
    admin.site.unregister(YourStoryEntry)
    admin.site.unregister(YourStoryCompetition)
    admin.site.unregister(LiveChat)
    admin.site.unregister(LiveChatResponse)
    admin.site.unregister(User)
except NotRegistered:
    pass

# Hide userprofile.admin fields by using the default django admin for User
admin.site.register(User, UserAdmin)

admin.site.unregister(Relation)
admin.site.register(Relation, HiddenModelAdmin)

# remove publisher models from admin
admin.site.unregister(publisher.models.Buzz)
admin.site.unregister(publisher.models.Facebook)
admin.site.unregister(publisher.models.Mobile)
admin.site.unregister(publisher.models.SocialBookmark)
admin.site.unregister(publisher.models.Twitter)
admin.site.unregister(publisher.models.Web)

# remove celery from admin
admin.site.unregister(djcelery.models.TaskState)
admin.site.unregister(djcelery.models.WorkerState)
admin.site.unregister(djcelery.models.IntervalSchedule)
admin.site.unregister(djcelery.models.CrontabSchedule)
admin.site.unregister(djcelery.models.PeriodicTask)

# remove south from admin
import south
admin.site.unregister(south.models.MigrationHistory)
