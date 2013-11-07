from django.contrib import admin
from django.contrib.contenttypes import generic

from jmbo.admin import ModelBaseAdmin
from mama.models import (Link, NavigationLink, SitePreferences, Banner,
                         DefaultAvatar)
from post.models import Post
from livechat.models import LiveChat
from preferences.admin import PreferencesAdmin
from jmboyourwords.admin import YourStoryEntryAdmin
from jmboyourwords.models import YourStoryEntry


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
        profile = obj.user.get_profile()
        return profile.mobile_number


admin.site.register(SitePreferences, PreferencesAdmin)
admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.unregister(YourStoryEntry)
admin.site.register(YourStoryEntry, MamaYourStoryEntryAdmin)
admin.site.register(DefaultAvatar, DefaultAvatarAdmin)
