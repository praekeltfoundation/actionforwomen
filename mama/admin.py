from django.contrib import admin
from jmbo.admin import ModelBaseAdmin
from mama.models import Link, NavigationLink, SitePreferences, Banner
from post.models import Post
from preferences.admin import PreferencesAdmin


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
    ]

class BannerAdmin(ModelBaseAdmin):

    list_display = ('title', 'thumbnail', 'schedule')

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
