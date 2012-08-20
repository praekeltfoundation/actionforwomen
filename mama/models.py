from datetime import date

from ckeditor.fields import RichTextField
from django.contrib.comments.models import Comment
from django.db import models
from django.db.models.signals import class_prepared
from django.dispatch import receiver
from likes.exceptions import CannotVoteException
from likes.signals import likes_enabled_test, can_vote_test
from mama.forms import RegistrationForm
from preferences.models import Preferences
import secretballot
from userprofile.models import AbstractProfileBase


class Link(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="A short descriptive title. Leave blank to use target's title.",
    )
    source = models.ForeignKey(
        'jmbo.ModelBase',
        related_name="link_target_set"
    )
    target = models.ForeignKey(
        'jmbo.ModelBase',
        related_name="link_source_set"
    )

    class Meta:
        ordering = ['-id',]

    def __unicode__(self):
        return self.title

class NavigationLink(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="A short descriptive title. Leave blank to use target's title.",
    )
    source = models.ForeignKey(
        'jmbo.ModelBase',
        related_name="navigation_link_target_set"
    )
    target = models.ForeignKey(
        'jmbo.ModelBase',
        related_name="navigation_link_source_set"
    )

    def __unicode__(self):
        return self.title


class SitePreferences(Preferences):
    __module__ = 'preferences.models'
    pregnancy_helpline_number = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    baby_helpline_number = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    hivaids_helpline_number = models.CharField(
        "HIV/Aids helpline number",
        max_length=64,
        blank=True,
        null=True
    )
    about = RichTextField(
        blank=True,
        null=True
    )
    terms = RichTextField(
        blank=True,
        null=True
    )
    contact_email_recipients = models.ManyToManyField(
        'auth.User',
        blank=True,
        null=True,
        help_text='Select users who will recieve emails sent via the contact form.'
    )

    class Meta:
        verbose_name_plural = "Site preferences"


class UserProfile(AbstractProfileBase):
    registration_form = RegistrationForm
    mobile_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
    )
    weeks_pregnant_signup = models.IntegerField(
        choices=((i, 'Week%s %s' % ('s' if i > 1 else '', i)) for i in range(1,43)),
        blank=True,
        null=True,

    )
    delivery_date = models.DateField(
        blank=True,
        null=True,
    )
    last_reset_date = models.DateField(
        blank=True,
        null=True,
        help_text='Last date on which user tried to reset her password.',
    )
    reset_count = models.IntegerField(
        blank=True,
        null=True,
        help_text='Number of times user has tried to reset her password on the last reset date.',
    )

    def is_prenatal(self):
        """
        Returns True if prenatal, otherwise False
        If no delivery date is specified it is assumed we are prenatal.
        """
        if not self.delivery_date:
            return True
        return date.today() < self.delivery_date
    
    def is_postnatal(self):
        """
        Returns True if postnatal, otherwise False
        If no delivery date is specified it is assumed we are prenatal.
        """
        if not self.delivery_date:
            return False
        return date.today() > self.delivery_date


@receiver(class_prepared)
def add_field(sender, **kwargs):
    """
    Monkey patch color field to Category model.
    """
    if sender.__name__ == 'Category':
        color_field = models.CharField(
            choices=(
                ("yorange", "Light Orange"),
                ("dorange", "Dark Orange"),
                ("maroon", "Maroon"),
                ("purple", "Purple"),
            ),
            max_length=64,
            blank=True,
            null=True,
            default='yorange',
            help_text="Color categorized content is styled with."
        )
        color_field.contribute_to_class(sender, "color")

secretballot.enable_voting_on(
    Comment,
)

likes_enabled_test.disconnect(sender=Comment)
@receiver(likes_enabled_test, sender=Comment)
def on_likes_enabled_test(sender, instance, request, **kwargs):
    return True

likes_enabled_test.disconnect(sender=Comment)
@receiver(can_vote_test, sender=Comment)
def on_can_vote_test(sender, instance, user, request, **kwargs):
    if instance.user == user:# or instance.ip_address == request.META['REMOTE_ADDR'] :
        raise CannotVoteException
    else:
        return True
