from datetime import date

from ckeditor.fields import RichTextField
from django.contrib.comments.models import Comment
from django.core.cache import cache
from django.db import models
from django.db.models.signals import class_prepared, post_save
from django.dispatch import receiver

from jmbo.models import ModelBase
from likes.exceptions import CannotVoteException
from likes.signals import likes_enabled_test, can_vote_test
from preferences.models import Preferences
from userprofile.models import AbstractProfileBase

from photologue.models import ImageModel
from mama.forms import RegistrationForm
from mama.constants import RELATION_TO_BABY_CHOICES, DATE_QUALIFIER_CHOICES


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

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['id', ]


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


class DefaultAvatar(ImageModel):
    """A set of avatars users can choose from"""
    pass


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
    alias = models.CharField(
        max_length=128,
        blank=True,
        null=True,
    )
    banned = models.BooleanField(
        help_text='Whether or not user is banned from posting comments.',
        default=False,
        blank=True,
    )
    decline_surveys = models.BooleanField(
        help_text='Whether or not user declined to paricipate in surveys.',
        default=False,
        blank=True,
    )
    origin = models.CharField(
        help_text='Where did this user register?',
        null=True,
        max_length=255
    )
    relation_to_baby = models.CharField(
        max_length=30,
        choices=RELATION_TO_BABY_CHOICES,
        default='mom_or_mom_to_be'
    )
    date_qualifier = models.CharField(
        max_length=20,
        choices=DATE_QUALIFIER_CHOICES,
        default='due_date'
    )
    unknown_date = models.BooleanField(
        help_text='Checked if the due date is unknown.',
        default=False,
        blank=True,
    )
    about_me = models.TextField(blank=True, null=True)
    baby_name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField('avatar', max_length=100, 
                               upload_to='users/profile', 
                               blank=True, null=True)

    def relation_description(self):
        """ 
        Returns the relationship of the registrant to the baby, taking into
        account the relationship selected, and date type selected.
        """
        if self.date_qualifier == 'birth_date':
            if self.relation_to_baby == 'mom_or_mom_to_be':
                return 'Mom'
            elif self.relation_to_baby == 'dad_or_dad_to_be':
                return 'Dad'
        elif self.date_qualifier == 'due_date':
            if self.relation_to_baby == 'mom_or_mom_to_be':
                return 'Mom to be'
            elif self.relation_to_baby == 'dad_or_dad_to_be':
                return 'Dad to be'
        return 'Family Member'

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


class Banner(ModelBase):
    url = models.CharField(
        max_length=256,
        help_text="Root relative URL to which the banner will redirect."
    )
    time_on = models.TimeField(
        blank=True,
        null=True,
        help_text="Time at which the banner will start displaying. If "
                  "either time on or time off is not specified the banner "
                  "will always be eligable for display (can be randomly selected)."
    )
    time_off = models.TimeField(
        blank=True,
        null=True,
        help_text="Time at which the banner will stop displaying. If either "
                  "time on or time off is not specified the banner will "
                  "always be eligable for display (can be randomly selected)."
    )

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


likes_enabled_test.disconnect(sender=Comment)
@receiver(likes_enabled_test, sender=Comment)
def on_likes_enabled_test(sender, instance, request, **kwargs):
    return True


likes_enabled_test.disconnect(sender=Comment)
@receiver(can_vote_test, sender=Comment)
def on_can_vote_test(sender, instance, user, request, **kwargs):
    if instance.user == user:
        raise CannotVoteException
    else:
        return True


@receiver(post_save)
def cache_clearer(instance, *args, **kwargs):
    """
    Clears the entire cache whenever a content object is changed/saved.
    """
    if isinstance(instance, ModelBase):
        cache.clear()
