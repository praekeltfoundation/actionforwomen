import uuid
from datetime import date

import ambient
from dateutil import parser
from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.forms.extras.widgets import SelectDateWidget
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe
import mama
from pml import forms as pml_forms
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

        message = "Hi %s. Follow this link to reset your MAMA password: http://%s%s" % (
            self.user.username,
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
        del self.fields['password2']
        self.fields.keyOrder = [
            'username',
            'mobile_number',
            'delivery_date',
            'password1',
            'tos',
        ]
        self.fields['mobile_number'].required = True
        self.fields['delivery_date'].required = True
        self.fields['delivery_date'].label = "What is your due date or baby's birthday?"
        self.fields['delivery_date'].widget = SelectDateWidget()
        self.fields['tos'].label = mark_safe('I accept the <a href="%s">terms '
                                             'and conditions</a> of use.'
                                             % reverse("terms"))

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        RegexValidator('^\d{10}$', message="Enter a valid mobile number in "
                       "the form 0719876543")(mobile_number)
        try:
            mama.models.UserProfile.objects.get(
                mobile_number__exact=mobile_number
            )
            raise ValidationError('A user with that mobile number already '
                                  'exists. <a href="%s">Forgotten your '
                                  'password?</a>' % reverse("password_reset"))
        except mama.models.UserProfile.DoesNotExist:
            return mobile_number


class ProfileForm(pml_forms.PMLForm):
    submit_text = "Register"
    username = pml_forms.PMLTextField(
        label="Username",
        help_text="This name will appear next to all your comments."
    )
    delivery_date = pml_forms.PMLTextField(
        label="What is your due date or baby's birthday?",
    )
    tos = pml_forms.PMLCheckBoxField(
        choices=(
            ("accept", 'I accept the terms and conditions of use.'),
        )
    )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['tos'] = pml_forms.PMLCheckBoxField(
            choices=(
                ("accept", mark_safe('I accept the <LINK href="%s">terms '
                                     'and conditions</LINK> of use.'
                                     % reverse("terms"))),
            )
        )

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data['delivery_date']
        try:
            delivery_date = parser.parse(delivery_date)
        except ValueError:
            raise ValidationError('Please enter a date in the format day/month/year(i.e. 17/8/2013).')

        return delivery_date
