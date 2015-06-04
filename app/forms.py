import uuid
from datetime import date
import time
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
from django.core.mail import EmailMessage, mail_managers

from PIL import Image
from django.utils.translation import ugettext as _

from pml import forms as pml_forms
from registration.forms import RegistrationFormTermsOfService
from jmboyourwords.models import YourStoryEntry
from userprofile import utils
import app

from app.tasks import send_sms
from app.constants import (
    RELATION_TO_BABY_CHOICES,
    DATE_QUALIFIER_CHOICES
)

GENDER_CHOICES=[
    ('', _('Select Gender')),
    ('male',_('Male')),
    ('female',_('Female')),
    ('other',_('Other'))
    ]
IDENTITY_CHOICES = [
    ('', _('Select Identity')),
    ('first_nations_status', _('First Nations Status')),
    ('first_nations_non_status', _('First Nations Non-Status')),
    ('inuit', _('Inuit')),
    ('metis', _('Metis')),
    ('non_aboriginal', _('Non-Aboriginal'))
    ]


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
            self.profile = app.models.UserProfile.objects.get(
                mobile_number__exact=mobile_number
            )
            self.user = self.profile.user
        except app.models.UserProfile.DoesNotExist:
            raise forms.ValidationError(_("Unable to find an account for the "
                                        "provided mobile number. Please try "
                                        "again."))
        # Fail if user has already reset password today more than once.
        if self.profile.last_reset_date == date.today() \
                and self.profile.reset_count >= 2:
            raise forms.ValidationError(_("You have already tried to reset "
                                        "your PIN today. Please wait "
                                        "for your SMS or try again tomorrow."))
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

        message = _(
            "Hi %(name)s. "
            "Follow this link to reset your PIN: http://%(domain)s%(url)s") % {
            'name': self.user.username,
            'domain': current_site.domain,
            'url': reverse(
                'password_reset_confirm',
                kwargs={'uidb36': uid, 'token': token}
            )
        }

        send_sms.delay(self.profile.mobile_number, message)


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField()


    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data['email']
        # Fail with invalid number.
        try:
            email = self.cleaned_data["email"]
            self.user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_("Unable to find an account for the "
                                        "provided email. Please try "
                                        "again."))
        return email
    def save(self, *args, **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """

        uid = int_to_base36(self.user.id)
        token = default_token_generator.make_token(self.user)
        current_site = get_current_site(kwargs['request'])

        message = _(
            "Hi %(name)s. "
            "Follow this link to reset your PIN: http://%(domain)s%(url)s") % {
            'name': self.user.username,
            'domain': current_site.domain,
            'url': reverse(
                'password_reset_confirm',
                kwargs={'uidb36': uid, 'token': token}
            )
        }

        subject = _("[A4W] Reset your PIN")
        recipients = [self.user.email]
        from_address = settings.FROM_EMAIL_ADDRESS
        mail = EmailMessage(
            subject,
            message,
            from_address,
            recipients,
            headers={'From': from_address, 'Reply-To': from_address}
        )
        mail.send(fail_silently=True)


class RegistrationForm(RegistrationFormTermsOfService):
    mobile_number = forms.CharField(
        max_length=64,
        required=False,
        label="Your mobile number"
    )
    alias = forms.CharField(
       label="Display Name",
       required=False
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(), required=False)
    year_of_birth = forms.IntegerField(
        label="Year of birth",
        required=False
    )
    identity = forms.ChoiceField(choices=IDENTITY_CHOICES, widget=forms.Select(), required=False)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # set up the form
        #del self.fields['email']
        del self.fields['password2']
        self.fields.keyOrder = [
            'username',
            #'email',
            'password1',
            'mobile_number',
            'tos',
            'gender',
            'alias',
            'year_of_birth',
            'identity',
        ]
        self.fields['username'].label = "Choose a username"
        self.fields['email'].label = "Choose email"
        self.fields['password1'].label = "Choose a PIN"

        self.fields['tos'].label = mark_safe('I accept the <a href="%s" style="text-decoration:underline;">terms '
                                             'and conditions</a> of use.'
                                             % reverse("terms"))

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        if mobile_number.startswith('1'):
            RegexValidator('^\d{11}$', message=_("Enter a valid mobile number in "
               "the form 14034228916"))(mobile_number)
        else:
            RegexValidator('^\d{10}$', message=_("Enter a valid mobile number in "
                   "the form 14034228916"))(mobile_number)
        try:
            app.models.UserProfile.objects.get(
                mobile_number__exact=mobile_number
            )
            error_msg_1 = _('A user with that mobile number already exists.')
            error_msg_2 = _('Forgotten your PIN?')
            raise ValidationError(error_msg_1 + ' <a href="%s">%s</a>' % (
                reverse("reset_password_email"),
                error_msg_2))
        except app.models.UserProfile.DoesNotExist:
            return mobile_number

    def clean_username(self):
        email = self.cleaned_data['username']
        RegexValidator('\w[\w\.-]*@\w[\w\.-]+\.\w+', message=_("Enter a valid email address."))(email)
        try:
            User.objects.get(
                email__exact=email
            )
            raise ValidationError(_('A user with that email already exists'))
        except User.DoesNotExist:
            return email

    def clean_gender(self):
        gender = self.cleaned_data['gender']
        return gender

    def clean_year_of_birth(self):
        year_of_birth = self.cleaned_data['year_of_birth']
        thisyear = time.localtime()[0]
        if year_of_birth > thisyear:
            raise ValidationError(u'Please enter a valid year')
        return year_of_birth

    def clean_identity(self):
        identity = self.cleaned_data['identity']
        return identity

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
    avatar = forms.ImageField(
        label="Upload Picture",
        required=False
    )

    username = forms.CharField(
        max_length=100,
        label="Username",
        required=False,
        widget=forms.HiddenInput()
    )
    first_name = forms.CharField(
        label="Name",
        required=False
    )
    last_name = forms.CharField(
        max_length=100,
        label="Surname",
        required=False
    )
    alias = forms.CharField(
       label="Alias",
       required=False
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(), required=False)
    year_of_birth = forms.IntegerField(
        label="Year of birth",
        required=False,
    )
    identity = forms.ChoiceField(choices=IDENTITY_CHOICES, widget=forms.Select(), required=False)
    engage_anonymously = forms.BooleanField(
        label="Engage Anonymously",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'username',
            'mobile_number',
            'avatar',
            'first_name',
            'last_name',
            'alias',
            'gender',
            'year_of_birth',
            'identity',
            'engage_anonymously',
        ]
        self.fields['username'].label = "Username"
        self.fields['last_name'].label = "Surname"
        self.fields['mobile_number'].label = "Mobile Number"
        self.fields['gender'].label = "Gender"

        # sort out some form display logic
        initial = kwargs['initial']

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        RegexValidator('^\d{10,11}$', message="Enter a valid mobile number in "
                       "the form 14034228916")(mobile_number)

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

    def clean_avatar(self):
        image = self.cleaned_data.get('avatar', False)
        try:
            img = Image.open(image)
            w, h = img.size
            max_width = max_height = 500
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    _('Please use an image that is smaller or equal to '
                      '500 x 500 pixels.'))
            main, sub = image.content_type.split('/')
            if not (main == 'image' and sub.lower() in ['jpeg', 'pjpeg', 'png', 'jpg']):
                raise forms.ValidationError(_('Please use a JPEG or PNG image.'))
            if len(image) > (500 * 1024):
                raise forms.ValidationError(_('Image file too large ( maximum 500KB )'))
        except AttributeError:
            pass
        return image

    def clean_last_name(self):
        """
        Validate that the username is alphanumeric and already exists
        """
        return self.cleaned_data['last_name']
    def clean_year_of_birth(self):
        year_of_birth = self.cleaned_data['year_of_birth']
        thisyear = time.localtime()[0]
        if year_of_birth > thisyear:
            raise ValidationError(u'Please enter a valid year')
        return year_of_birth

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
        return cleaned_data

    @property
    def default_avatars(self):
        return app.models.DefaultAvatar.objects.all()


class DueDateForm(forms.Form):
    due_date = forms.DateField(
        required = True,
        label = "Due Date",
        widget = SelectDateWidget()
    )


class ProfileForm(pml_forms.PMLForm):
    submit_text = "Register"

    username = pml_forms.PMLTextField(
        label="Alias",
        help_text="This name will appear next to all your comments."
    )
    last_name = pml_forms.PMLTextField(
        label="Alias",
        help_text="This is the last name or surname"
    )
    tos = pml_forms.PMLCheckBoxField(
        choices=(
            (
                "accept",
                mark_safe("""I accept the <LINK href="/terms/"><TEXT>terms and conditions</TEXT></LINK> of use.""")
            ),
        ))

    def clean(self):
        """
        Check that the birth date is provided, if the person selected birth
        date as the date type.
        Check that the due date is provided or the unknown check box is checked
        if due date is selected as the date type.
        """
        cleaned_data = super(ProfileForm, self).clean()
        return cleaned_data


class VLiveProfileEditForm(pml_forms.PMLForm):
    """
    The VLive form to edit all options in the member's full profile.
    """
    submit_text="Save"

    username = pml_forms.PMLTextField(
        label="Alias",
        help_text="This name will appear next to all your comments."
    )
    last_name = pml_forms.PMLTextField(
        label="Alias",
        help_text="This is the last name or surname"
    )

    def __init__(self, *args, **kwargs):
        super(VLiveProfileEditForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(VLiveProfileEditForm, self).clean()
        return cleaned_data


class VLiveDueDateForm(forms.Form):
    due_date = pml_forms.PMLTextField(
        label="What is your due date? (yyyy-mm-dd)",
        required=False
    )

    def clean_due_date(self):
        """
        Check that the due date is provided and correct.
        """
        try:
            due_date = self.cleaned_data['due_date']
            due_date = parser.parse(due_date)
        except (KeyError, ValueError):
            raise forms.ValidationError(
                    "The due date was entered incorrectly.")
        return due_date


class MomsStoryEntryForm(forms.ModelForm):
    class Meta:
        model = YourStoryEntry
        exclude = ('user', 'your_story_competition', 'terms')

    def clean_terms(self):
        return True

class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=64)
    email = forms.EmailField()
    message = forms.CharField(
        widget=forms.Textarea,
    )
