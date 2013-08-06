from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from mama.urls import urlpatterns
from mama.views import ProfileView


urlpatterns = patterns('',
    (r'^djga/', include('google_analytics.urls')),
    url(
        r'^accounts/register/$',
        login_required(ProfileView.as_view()),
        name='registration_register'
    ),
    (r'^survey/', 
        include('mama.sites.vlive.survey_urls', namespace='survey')),
) + urlpatterns
