from django.contrib import admin
from django.contrib.contenttypes import generic

from jmbo.admin import ModelBaseAdmin
from mama.models import Link, NavigationLink, SitePreferences
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


admin.site.register(SitePreferences, PreferencesAdmin)
admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
