from django import forms

from pml.forms import PMLForm
from pml.forms.fields import PMLTextField, PMLCheckBoxField, PMLHiddenField


class PMLYourStoryForm(PMLForm):
    """ Submit your story form for the Vlive site
    """
    next = PMLHiddenField()
    name = PMLHiddenField()
    email = PMLHiddenField()
    competition_id = PMLHiddenField()
    text = PMLTextField(required=True)
    terms = PMLCheckBoxField(
        required=False,
        choices=(("accept", "I accept the terms and conditions"),)
    )

    def clean_terms(self):
        terms = self.cleaned_data['terms']
        if terms == False:
            raise ValidationError(u'You must agree to the terms and conditions')

        return terms
