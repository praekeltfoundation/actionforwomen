from django.utils.translation import ugettext_lazy as _
from django import forms

from pml.forms import PMLForm
from pml.forms.fields import PMLRadioField, PMLHiddenField

from survey.forms import _SURVEY_CHOICES, SurveyQuestionMixin
from survey.models import MultiChoiceQuestion


class PMLSurveyChoiceForm(PMLForm):
    """ Choose how to proceed with a survey on the VLIVE site
    """
    survey_id = PMLHiddenField()
    proceed_choice = PMLRadioField(
        choices=_SURVEY_CHOICES,
        label=_('Would you like to participate?'),
        initial='now')


class PMLSurveyQuestionForm(SurveyQuestionMixin, PMLForm):
    """ Display the options and capture the answer for one question in the
        survey on the VLIVE site.
    """
    survey_id = PMLHiddenField()
    question_id = PMLHiddenField()
    question = PMLRadioField()

    def full_clean(self):
        fld_survey_id = self.fields['survey_id']
        fld_question_id = self.fields['question_id']

        survey_id = fld_survey_id.widget.value_from_datadict(self.data,
                self.files, self.add_prefix('survey_id'))
        question_id = fld_question_id.widget.value_from_datadict(self.data,
                self.files, self.add_prefix('question_id'))
        question = MultiChoiceQuestion.objects.get(pk=question_id)
        self.update_the_form(survey_id, question)
        
        super(PMLSurveyQuestionForm, self).full_clean()
