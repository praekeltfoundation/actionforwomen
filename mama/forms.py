import uuid
from datetime import date

import ambient
from dateutil import parser
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
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


from mama.constants import RELATION_TO_BABY_CHOICES, DATE_QUALIFIER_CHOICES

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
    mobile_number = forms.CharField(
        max_length=64, 
        required=True,
        label="Your mobile number"
    )
    relation_to_baby = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=RELATION_TO_BABY_CHOICES,
        label='Are you a...',
        initial='mom_or_mom_to_be'
    )

    date_qualifier = forms.ChoiceField(
        widget=forms.RadioSelect(),
        initial='due_date',
        choices=DATE_QUALIFIER_CHOICES,
        label="Please enter your baby's birth day or due date or select \
            unknown if you are not sure of the due date"
    )
    delivery_date = forms.DateField(
        required=False,
        label="",
        widget=SelectDateWidget()
    )
    unknown_date = forms.BooleanField(
        required=False,
        label='Unknown'
    )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        del self.fields['email']
        del self.fields['password2']
        self.fields.keyOrder = [
            'username',
            'password1',
            'mobile_number',
            'relation_to_baby',
            'date_qualifier',
            'delivery_date',
            'unknown_date',
            'tos',
        ]
        self.fields['username'].label = "Choose a username"
        self.fields['password1'].label = "Choose a password"
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

    def clean(self):
        """
        Check that the birth date is provided, if the person selected birth
        date as the date type.
        Check that the due date is provided or the unknown check box is checked
        if due date is selected as the date type.
        """
        cleaned_data = super(RegistrationForm, self).clean()
        delivery_date = cleaned_data['delivery_date']
        date_qualifier = cleaned_data['date_qualifier']
        try:
            unknown_date = cleaned_data['unknown_date']
        except KeyError:
            pass
        if date_qualifier == 'birth_date' and delivery_date is None:
            msg = 'You need to provide a birth date'
            self._errors['delivery_date'] = self.error_class([msg])
            del cleaned_data['delivery_date']
        elif date_qualifier == 'due_date' and delivery_date is None \
                and not unknown_date:
            msg = "Either provide a due date, or check the \
                  'Unknown' check box below the date."
            self._errors['delivery_date'] = self.error_class([msg])
            del cleaned_data['delivery_date']
        return cleaned_data


class EditProfileForm(RegistrationForm):
    """
    The form to edit all options in the member's full profile.
    """
    about_me = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    baby_name = forms.CharField(
        max_length=100,
        label="Name",
        required=False
    )
    baby_has_been_born = forms.BooleanField(
        label="Baby has been born",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['date_qualifier'].widget = forms.HiddenInput()
        self.fields.keyOrder = [
            'username',
            'mobile_number',
            'relation_to_baby',
            'about_me',
            'baby_name',
            'date_qualifier',
            'delivery_date',
            'unknown_date',
            'baby_has_been_born'
        ]
        self.fields['username'].label = "Username"
        self.fields['mobile_number'].label = "Mobile Number"
        self.fields['relation_to_baby'].label = 'I am'

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        RegexValidator('^\d{10}$', message="Enter a valid mobile number in "
                       "the form 0719876543")(mobile_number)
        return mobile_number

    def clean_username(self):
        """
        Validate that the username is alphanumeric and already exists
        """
        try:
            user = User.objects.get(
                username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            raise forms.ValidationError(
                "Could not find a user with this username.")
        return self.cleaned_data['username']

    def clean(self):
        """
        Check that the birth date is provided, if the person selected birth
        date as the date type, of if she indicated that the baby has been
        born.
        Check that the due date is provided or the unknown check box is checked
        if due date is selected as the date type. If they checked the baby has
        been born checkbox, check that a birth date was provided.
        """
        cleaned_data = super(EditProfileForm, self).clean()
        delivery_date = cleaned_data['delivery_date']
        date_qualifier = cleaned_data['date_qualifier']
        if date_qualifier == 'due_date':
            unknown_date = cleaned_data['unknown_date']
            baby_has_been_born = cleaned_data['baby_has_been_born']
        if date_qualifier == 'birth_date' and delivery_date is None:
            msg = 'You need to provide a birth date'
            self._errors['delivery_date'] = self.error_class([msg])
            del cleaned_data['delivery_date']
        elif date_qualifier == 'due_date':
            if baby_has_been_born and delivery_date is None:
                msg = "You have indicated that the baby has been born. \
                       Please provide the birth date in the due date field \
                       above."
                self._errors['delivery_date'] = self.error_class([msg])
                del cleaned_data['delivery_date']
            elif not unknown_date and delivery_date is None:
                msg = "Either provide a due date, or check the \
                      'Unknown' check box below the date."
                self._errors['delivery_date'] = self.error_class([msg])
                del cleaned_data['delivery_date']
        return cleaned_data

    @property
    def default_avatars(self):
        return mama.models.DefaultAvatar.objects.all()


class DueDateForm(forms.Form):
    due_date = forms.DateField(
        required = True,
        label = "Due Date",
        widget = SelectDateWidget()
    )


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
