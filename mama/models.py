from datetime import datetime, timedelta

from ckeditor.fields import RichTextField
from django.db import models
from django.db.models.signals import class_prepared, pre_save
from django.dispatch import receiver
from preferences.models import Preferences
from userprofile.models import AbstractProfileBase
from mama.forms import RegistrationForm


class Link(models.Model):
    title = models.CharField(
        max_length=256,
        help_text='A short descriptive title.',
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

    class Meta:
        verbose_name_plural = "Site preferences"


class UserProfile(AbstractProfileBase):
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
    computed_delivery_date = models.DateField(
        blank=True,
        null=True,
    )
    registration_form = RegistrationForm


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


@receiver(pre_save, sender=UserProfile)
def compute_delivery_date(sender, instance, **kwargs):
    if instance.weeks_pregnant_signup:
        weeks_left = 42 - instance.weeks_pregnant_signup
        instance.computed_delivery_date = datetime.now() + timedelta(days=7 * weeks_left)
