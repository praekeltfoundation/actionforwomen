from datetime import datetime
from dateutil.relativedelta import *

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.comments.models import Comment
from django.contrib.admin.sites import NotRegistered
from django.contrib.contenttypes.models import ContentType

from jmbo.admin import ModelBaseAdmin
from secretballot.models import Vote
from mama.models import (Link, NavigationLink, SitePreferences, Banner,
                         DefaultAvatar)
from post.models import Post
from livechat.models import LiveChat
from preferences.admin import PreferencesAdmin
from jmboyourwords.admin import YourStoryEntryAdmin
from jmboyourwords.models import YourStoryEntry
from moderator.admin import CommentAdmin
from category.models import Category


class LinkInline(admin.TabularInline):
    model = Link
    fk_name = 'source'


class NavigationLinkInline(admin.TabularInline):
    model = NavigationLink
    fk_name = 'source'


class PostAdmin(ModelBaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        LinkInline,
        NavigationLinkInline
    ]


class BannerAdmin(ModelBaseAdmin):

    list_display = (
        'title', 'description', 'thumbnail', 'schedule', '_actions')

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
            return """<img src="%s" height="48" width="48" />""" % obj.image.url
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
        # Find the dates for the current week, starting last Sunday and ending
        # next Saturday
        NOW = datetime.now()
        start_sunday = NOW + relativedelta(weekday=SU(-1),
                                           hour=0, minute=0,
                                           second=0, microsecond=0)
        end_saturday = NOW + relativedelta(weekday=SA(+1),
                                           hour=0, minute=0,
                                           second=0, microsecond=0, 
                                           microseconds=-1)

        # Subtract the amount of weeks in the past.
        try:
            weeks_ago = int(self.value())
        except TypeError:
            weeks_ago = 0

        if weeks_ago > 0:
            start_sunday = start_sunday + relativedelta(weeks=-weeks_ago)
            end_saturday = end_saturday + relativedelta(weeks=-weeks_ago)

        if weeks_ago < 2:
            # Filter the questions between the date range
            queryset = queryset.filter(submit_date__range=(start_sunday, 
                                                           end_saturday,))
        else:
            # Filter all the older questions.
            queryset = queryset.filter(submit_date__lt=(start_sunday)) 

        # Work out the vote count for the questions, to sort by the most liked
        # questions, i.e. questions with the most votes. (This is taken from the
        # MostLikedItem view modifier item in jmbo)
        queryset = queryset.extra(
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
                    ContentType.objects.get_for_model(Comment).id
                )
            }
        )
        return queryset


class AskMamaQuestionAdmin(CommentAdmin):
    """ Add a filter to filter out 'This week's favourite stories' in CMS
    """
    list_display = ('comment_text', 'user', 'submit_date',
                    'classification', 'moderator_replied', 'is_removed')
    list_filter = (WeeklyFilter,)
    date_hierarchy = None

    def queryset(self, request):
        """ Filter the questions that have been submitted this week in the
            AskMama section.
        """
        latest_pinned = self.get_askmama_latest_pinned_post()
        pct = ContentType.objects.get_for_model(latest_pinned.__class__)

        # Filter the comments linked to the post
        questions = AskMamaQuestion.objects.filter(
            content_type=pct,
            object_pk=latest_pinned.id)
        questions = questions.exclude(is_removed=True)

        # leave out the moderator answers
        questions = questions.exclude(user__is_staff=True)

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


admin.site.register(SitePreferences, PreferencesAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(DefaultAvatar, DefaultAvatarAdmin)

try:
    admin.site.unregister(Post)
except NotRegistered:
    pass
admin.site.register(Post, PostAdmin)

try:
    admin.site.unregister(YourStoryEntry)
except NotRegistered:
    pass
admin.site.register(YourStoryEntry, MamaYourStoryEntryAdmin)

admin.site.register(AskMamaQuestion, AskMamaQuestionAdmin)
