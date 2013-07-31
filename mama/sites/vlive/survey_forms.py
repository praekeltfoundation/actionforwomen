from django.utils.translation import ugettext_lazy as _
from django import forms

from pml.forms import PMLForm
from pml.forms.fields import PMLRadioField

from survey.forms import _SURVEY_CHOICES


class PMLSurveyChoiceForm(PMLForm):
    """ Choose how to proceed with a survey on the VLIVE site
    """
    survey_id = forms.Field(widget=forms.HiddenInput)
    proceed_choice = PMLRadioField(
        choices=_SURVEY_CHOICES,
        label=_('Would you like to participate?'),
        initial='now')


class PMLSurveyQuestionForm(PMLForm):
    """ Display the options and capture the answer for one question in the
        survey on the VLIVE site.
    """
    survey_id = forms.Field(widget=forms.HiddenInput)
    question_id = forms.Field(widget=forms.HiddenInput)
    question = PMLRadioField()
