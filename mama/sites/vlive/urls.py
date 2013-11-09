from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from mama.urls import urlpatterns
from mama.views import ProfileView, VLiveEditProfileEdit, BannerView


urlpatterns = patterns('',
    (r'^djga/', include('google_analytics.urls')),
    url(
        r'^accounts/register/$',
        login_required(ProfileView.as_view()),
        name='registration_register'
    ),
    url(
        r'^edit/myprofile/$',
        login_required(VLiveEditProfileEdit.as_view()),
        name='edit_my_profile'
    ),
    (r'^survey/',
        include('mama.sites.vlive.survey_urls', namespace='survey')),
    (r'^yourwords/',
        include('mama.sites.vlive.yw_urls')),
    (r'^carousel\.xml$', BannerView.as_view()),
) + urlpatterns
