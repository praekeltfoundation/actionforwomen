from django.contrib import admin
from jmbo.admin import ModelBaseAdmin
from mama.models import FeaturedContent


class FeaturedContentAdmin(ModelBaseAdmin):
    def queryset(self, request):
        return self.model.objects.filter(categories__slug='featured')

admin.site.register(FeaturedContent, FeaturedContentAdmin)
