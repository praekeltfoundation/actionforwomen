from django.db import models
from django.db.models.signals import class_prepared
from django.dispatch import receiver
from preferences.models import Preferences


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
        max_length=64
    )
    baby_helpline_number = models.CharField(
        max_length=64
    )
    hivaids_helpline_number = models.CharField(
        "HIV/Aids helpline number",
        max_length=64
    )

    class Meta:
        verbose_name_plural = "Site preferences"


@receiver(class_prepared)
def add_field(sender, **kwargs):
    """
    Monkey patch color field to Category model.
    """
    if sender.__name__ == 'Category':
        color_field = models.CharField(
            choices=(
                ("purple", "Purple"),
                ("maroon", "Maroon"),
                ("yorange", "Light Orange"),
                ("dorange", "Dark Orange"),
            ),
            max_length=64,
            blank=True,
            null=True,
            default='yorange',
            help_text="Color categorized content is styled with."
        )
        color_field.contribute_to_class(sender, "color")
