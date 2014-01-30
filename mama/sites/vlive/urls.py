from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from mama.urls import urlpatterns
from mama.views import ProfileView, VLiveEditProfile, BannerView


urlpatterns = patterns('',
    (r'^djga/', include('google_analytics.urls')),
    url(
        r'^accounts/register/$',
        login_required(ProfileView.as_view()),
        name='registration_register'
    ),
    url(
        r'^edit/myprofile/$',
        login_required(VLiveEditProfile.as_view()),
        name='edit_vlive_profile'
    ),
    (r'^survey/',
        include('mama.sites.vlive.survey_urls', namespace='survey')),
    (r'^yourwords/',
        include('mama.sites.vlive.yw_urls')),
    url(
        r'^vlivebanner/(?P<banner_type>[\w]+)/$',
        BannerView.as_view(),
        name='banner'
    ),
) + urlpatterns
