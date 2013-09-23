from django.contrib import admin
from django.contrib.contenttypes import generic

from jmbo.admin import ModelBaseAdmin
from mama.models import (Link, NavigationLink, SitePreferences, Banner,
                         DefaultAvatar)
from post.models import Post
from livechat.models import LiveChat
from preferences.admin import PreferencesAdmin


# class LiveChatInlineAdmin(generic.GenericStackedInline):
#     model = LiveChat
#     max_num = 1     # limit the livechat objects to 1 instance
#     extra = 0
#     fields = (
#         'title',
#         'subtitle',
#         'description',
#         'comments_closed',
#         'likes_closed',
#     )


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
        # LiveChatInlineAdmin
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


class DefaultAvatarAdmin(admin.ModelAdmin):
    list_display = ('_image',)

    def _image(self, obj):
        # todo: use correct photologue scale
        if obj.image:
            return """<img src="%s" height="48" width="48" />""" % obj.image.url
        return ""
    _image.short_description = 'Image'
    _image.allow_tags = True


admin.site.register(SitePreferences, PreferencesAdmin)
admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(DefaultAvatar, DefaultAvatarAdmin)
