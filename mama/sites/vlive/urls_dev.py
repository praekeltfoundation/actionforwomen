from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^mama/', include('mama.sites.vlive.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^mama/media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )