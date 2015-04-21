from django.conf.urls.defaults import patterns, url

from mama.sites.vlive.yw_views import PMLYourStoryView


urlpatterns = patterns('',
    url(r'^(?P<competition_id>\d+)/$',\
        PMLYourStoryView.as_view(),
        name='your_story'),
)
