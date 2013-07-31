from django.views.generic.edit import FormView

from survey.views import ChooseActionFormView, SurveyFormView
from mama.sites.vlive.survey_forms import (
    PMLSurveyChoiceForm, 
    PMLSurveyQuestionForm
)


class PMLChooseActionFormView(ChooseActionFormView):
    """ Present the 'Now', 'Later', 'Decline' choices to the user for the
        applicable questionnaire on the VLIVE site.
    """
    template_name = "vlive/survey/survey_choice.html"
    form_class = PMLSurveyChoiceForm


class PMLSurveyFormView(SurveyFormView):
    """ Display the next available question in the questionnaire to the user.
        If no more questions, redirect to the 'Thank you' page for the
        applicable questionnaire. On the VLIVE site.
    """
    template_name = "vlive/survey/survey_form.html"
    form_class = PMLSurveyQuestionForm

