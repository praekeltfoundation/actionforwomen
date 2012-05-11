from django.contrib import admin
from jmbo.admin import ModelBaseAdmin
from mama.models import Link, SitePreferences
from post.models import Post
from preferences.admin import PreferencesAdmin


class LinkInline(admin.TabularInline):
    model = Link
    fk_name = 'source'


class PostAdmin(ModelBaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        LinkInline,
    ]


admin.site.register(Link)
admin.site.register(SitePreferences, PreferencesAdmin)
admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
