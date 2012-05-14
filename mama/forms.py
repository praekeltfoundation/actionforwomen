from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from registration.forms import RegistrationFormTermsOfService
from userprofile import utils


class PasswordResetForm(forms.Form):
    mobile_number = forms.CharField(max_length=64)


class RegistrationForm(RegistrationFormTermsOfService):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        class ProfileModelForm(forms.ModelForm):
            class Meta:
                fields = ('mobile_number', 'weeks_pregnant_signup')
                model = utils.get_profile_model()
        self.fields.update(ProfileModelForm().fields)
        self.fields.keyOrder = [
            'username',
            'email',
            'mobile_number',
            'weeks_pregnant_signup',
            'password1',
            'password2',
            'tos',
        ]
        self.fields['email'].label = 'Email address'
        self.fields['mobile_number'].required = True
        self.fields['weeks_pregnant_signup'].required = True
        self.fields['weeks_pregnant_signup'].label = 'How long have you been pregnant?'
        self.fields['weeks_pregnant_signup'].choices = [('', 'Select the number of weeks')] + self.fields['weeks_pregnant_signup'].choices[1:]
        self.fields['password2'].label = 'Confirm your password'
        self.fields['tos'].label = mark_safe('I accept the <a href="%s">terms and conditions</a> of use.' % reverse("terms"))
