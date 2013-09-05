from django.contrib import admin
from django.contrib.contenttypes import generic

from jmbo.admin import ModelBaseAdmin
from mama.models import Link, NavigationLink, SitePreferences, Banner
from post.models import Post
from livechat.models import LiveChat
from preferences.admin import PreferencesAdmin


class LiveChatInlineAdmin(generic.GenericTabularInline):
    model = LiveChat
    max_num = 1     # limit the livechat objects to 1 instance
    extra = 0

class LinkInline(admin.TabularInline):
    model = Link
    fk_name = 'source'

class NavigationLinkInline(admin.TabularInline):
    model = NavigationLink
    fk_name = 'source'


class PostAdmin(ModelBaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        LinkInline,
        NavigationLinkInline,
        LiveChatInlineAdmin
    ]

class BannerAdmin(ModelBaseAdmin):

    list_display = (
        'title', 'description', 'thumbnail', 'schedule', 'state')

    def thumbnail(self, obj, *args, **kwargs):
        return '<img src="%s" />' % (obj.image.url,)
    thumbnail.allow_tags = True

    def schedule(self, obj, *args, **kwargs):
        if(obj.time_on and obj.time_off):
            return 'Randomly selected by Vlive between %s and %s' % (
                obj.time_on, obj.time_off)
        return 'Randomly selected by Vlive'


admin.site.register(SitePreferences, PreferencesAdmin)
admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
admin.site.register(Banner, BannerAdmin)
