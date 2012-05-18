from django.contrib import admin
from jmbo.admin import ModelBaseAdmin
from mama.models import Link, NavigationLink, SitePreferences
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


admin.site.register(SitePreferences, PreferencesAdmin)
admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
