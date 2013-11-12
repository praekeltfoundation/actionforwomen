from django import forms

from pml.forms import PMLForm
from pml.forms.fields import PMLTextField, PMLCheckBoxField, PMLHiddenField


class PMLYourStoryForm(PMLForm):
    """ Submit your story form for the Vlive site
    """
    next = PMLHiddenField()
    name = PMLHiddenField()
    email = PMLHiddenField()
    text = PMLTextField(required=True)
    terms = PMLCheckBoxField()

    def clean_terms(self):
        terms = self.cleaned_data['terms']
        if terms == False:
            raise ValidationError(u'You must agree to the terms and conditions')

        return terms
