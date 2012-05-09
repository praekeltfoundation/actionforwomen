from django.contrib import admin
from jmbo.admin import ModelBaseAdmin
from mama.models import Link
from post.models import Post


class LinkInline(admin.TabularInline):
    model = Link
    fk_name = 'source'


class PostAdmin(ModelBaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        LinkInline,
    ]

admin.site.register(Link)
admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
