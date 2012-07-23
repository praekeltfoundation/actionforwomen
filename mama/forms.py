import ambient
from datetime import date
from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.forms.extras.widgets import SelectDateWidget
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe
import mama
from registration.forms import RegistrationFormTermsOfService
from userprofile import utils


class ContactForm(forms.Form):
    mobile_number = forms.CharField(max_length=64)
    message = forms.CharField(
        widget=forms.Textarea,
        label="Please use the field below to send us a message."
    )


class PasswordResetForm(PasswordResetForm):
    mobile_number = forms.CharField(max_length=64)

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        del self.fields['email']

    def clean_mobile_number(self):
        """
        Validates that an active user exists with the given email address.
        """
        mobile_number = self.cleaned_data['mobile_number']
        # Fail with invalid number.
        try:
            self.profile = mama.models.UserProfile.objects.get(
                mobile_number__exact=mobile_number
            )
            self.user = self.profile.user
        except mama.models.UserProfile.DoesNotExist:
            raise forms.ValidationError("Unable to find an account for the "
                                        "provided mobile number. Please try "
                                        "again.")
        # Fail if user has already reset password today more than once.
        if self.profile.last_reset_date == date.today() \
                and self.profile.reset_count >= 2:
            raise forms.ValidationError("You have already tried to reset "
                                        "your password today. Please wait "
                                        "for your SMS or try again tomorrow.")
        return mobile_number

    def save(self, *args, **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        # Before we do anything else update reset counts for throttling.
        if self.profile.last_reset_date == date.today():
            self.profile.reset_count += 1
        else:
            self.profile.last_reset_date = date.today()
            self.profile.reset_count = 1
        self.profile.save()

        # Generate message containing url with users token.
        uid = int_to_base36(self.user.id)
        token = default_token_generator.make_token(self.profile.user)
        current_site = get_current_site(kwargs['request'])
        message = "Follow this link to reset your %s password: http://%s%s" % (
            current_site.name,
            current_site.domain,
            reverse(
                'password_reset_confirm',
                kwargs={'uidb36': uid, 'token': token}
            )
        )

        # Send the message using Ambient's gateway.
        sms = ambient.AmbientSMS(
            settings.AMBIENT_API_KEY,
            settings.AMBIENT_GATEWAY_PASSWORD
        )
        sms.sendmsg(message, [self.profile.mobile_number, ])


class RegistrationForm(RegistrationFormTermsOfService):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        class ProfileModelForm(forms.ModelForm):
            class Meta:
                fields = ('mobile_number', 'delivery_date')
                model = utils.get_profile_model()
        self.fields.update(ProfileModelForm().fields)
        del self.fields['email']
        self.fields.keyOrder = [
            'username',
            'mobile_number',
            'delivery_date',
            'password1',
            'password2',
            'tos',
        ]
        self.fields['mobile_number'].required = True
        self.fields['delivery_date'].required = True
        self.fields['delivery_date'].label = 'What is your due date'
        self.fields['delivery_date'].widget = SelectDateWidget()
        self.fields['password2'].label = 'Confirm your password'
        self.fields['tos'].label = mark_safe('I accept the <a href="%s">terms'
                                             'and conditions</a> of use.'
                                             % reverse("terms"))

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        RegexValidator('^27\d{9}$', message="Enter a valid mobile number in the form 27719876543")(mobile_number)
        return mobile_number
