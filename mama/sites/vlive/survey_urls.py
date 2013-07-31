from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

from survey.views import (CheckForQuestionnaireView, SurveyThankyouView,
                          SurveyExitView)
from mama.sites.vlive.survey_views import (
    PMLChooseActionFormView,
    PMLSurveyFormView
)

urlpatterns = patterns(
    '',
    url(
        r'^check-for-survey/$',
        login_required(CheckForQuestionnaireView.as_view()),
        name='check_for_survey'
    ),
    url(
        r'^survey-action/(?P<survey_id>\d+)/$',
        login_required(PMLChooseActionFormView.as_view()),
        name='survey_action'
    ),
    url(
        r'^survey/(?P<survey_id>\d+)/$',
        login_required(PMLSurveyFormView.as_view()),
        name='survey_form'
    ),
    url(
        r'^thank-you/(?P<survey_id>\d+)/$',
        login_required(SurveyThankyouView.as_view()),
        name='thankyou_page'
    ),
    url(
        r'^exit/$',
        login_required(SurveyExitView.as_view()),
        name='exit_page'
    ),
)
