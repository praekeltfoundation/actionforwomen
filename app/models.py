from datetime import date, datetime

from ckeditor.fields import RichTextField
from django.contrib.comments.models import Comment
from django.core.cache import cache
from django.db import models
from django.db.models.signals import class_prepared, post_save
from django.dispatch import receiver

from likes.exceptions import CannotVoteException
from likes.signals import likes_enabled_test, can_vote_test
from jmbo.models import ModelBase
from preferences.models import Preferences
from userprofile.models import AbstractProfileBase
from photologue.models import ImageModel
from jmboyourwords.models import YourStoryCompetition
from app.forms import RegistrationForm
from post.models import Post
from category.models import Category

from app.constants import (
    RELATION_TO_BABY_CHOICES,
    FULL_DATE_QUALIFIER_CHOICES
)


class StoryPost(Post):
    primary_category_slug = 'stories'

    class Meta:
        app_label = 'post'
        proxy = True
        verbose_name = 'Stories'
        verbose_name_plural = 'Stories'

    def save(self, *args, **kwargs):
        if not self.primary_category:
            self.primary_category = Category.objects.get(
                slug=self.primary_category_slug)
        super(StoryPost, self).save(*args, **kwargs)


class SupportPost(Post):
    primary_category_slug = 'support'

    class Meta:
        app_label = 'post'
        proxy = True
        verbose_name = 'Support'
        verbose_name_plural = 'Support'

    def save(self, *args, **kwargs):
        if not self.primary_category:
            self.primary_category = Category.objects.get(
                slug=self.primary_category_slug)
        super(SupportPost, self).save(*args, **kwargs)


class FAQPost(Post):
    primary_category_slug = 'faq'

    class Meta:
        app_label = 'post'
        proxy = True
        verbose_name = 'FAQs'
        verbose_name_plural = 'FAQs'

    def save(self, *args, **kwargs):
        if not self.primary_category:
            self.primary_category = Category.objects.get(
                slug=self.primary_category_slug)
        super(FAQPost, self).save(*args, **kwargs)


class CelebrityPost(Post):
    primary_category_slug = 'celebrity'

    class Meta:
        app_label = 'post'
        proxy = True
        verbose_name = 'Celebrities'
        verbose_name_plural = 'Celebrities'

    def save(self, *args, **kwargs):
        if not self.primary_category:
            self.primary_category = Category.objects.get(
                slug=self.primary_category_slug)
        super(CelebrityPost, self).save(*args, **kwargs)


class FactPost(Post):
    primary_category_slug = 'fact'

    class Meta:
        app_label = 'post'
        proxy = True
        verbose_name = 'Facts'
        verbose_name_plural = 'Facts'

    def save(self, *args, **kwargs):
        if not self.primary_category:
            self.primary_category = Category.objects.get(
                slug=self.primary_category_slug)
        super(FactPost, self).save(*args, **kwargs)


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
    about = RichTextField(
        blank=True,
        null=True
    )
    terms = RichTextField(
        blank=True,
        null=True
    )
    faqs = RichTextField(
        blank=True,
        null=True
    )
    comment_terms = RichTextField(
        blank=True,
        null=True
    )
    comment_report_confirm = RichTextField(
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

    comment_banned_patterns = models.TextField(
        blank=True,
        null=True,
        help_text='Comments containing these words or regular'
                  'expressions(one per line) will not be allowed to be posted.'
    )
    comment_silenced_patterns = models.TextField(
        blank=True,
        null=True,
        help_text='Sections or words in comments containing these words or '
                  'regular expressions(one per line) will be blocked out with '
                  'stars.'
    )
    commenting_time_on = models.TimeField(
        blank=True,
        null=True,
        help_text="Time after which users are allowed to post comments."
                  "If either time on or time off is not specified comments "
                  "will be allowed at any time."
    )
    commenting_time_off = models.TimeField(
        blank=True,
        null=True,
        help_text="Time after which users are not allowed to post comments "
                  "(until time on below). If either time on or time off is "
                  "not specified comments will be allowed at any time."
    )


    def comments_open(self, now=None):
        if not now:
            now = datetime.now().time()
        # Commenting is always allowed if both time on and time off
        # is not provided
        if not self.commenting_time_on:
            return True
        if not self.commenting_time_off:
            return True

        if self.commenting_time_on < self.commenting_time_off:
            return self.commenting_time_on < now < self.commenting_time_off

        if self.commenting_time_on > self.commenting_time_off:
            return now > self.commenting_time_on or now < self.commenting_time_off

        return True


class DefaultAvatar(ImageModel):
    """A set of avatars users can choose from"""
    pass


class UserProfile(AbstractProfileBase):
    """ The mama user profile model
    """
    registration_form = RegistrationForm

    # TODO: This could be a security risk, as password reset depends on a
    # mobile number to match a number in a user profile. So, this field should
    # not be optional. This number should also be unique across profiles.
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

    last_banned_date = models.DateField(
        help_text='The Date on which the user was banned',
        blank=True,
        null=True,
    )

    ban_duration = models.IntegerField(
        help_text='The length of time in days the user will be banned',
        blank=True,
        null=True,
    )

    accepted_commenting_terms = models.BooleanField(
        help_text='If a user has accepted the new commenting terms',
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
        choices=FULL_DATE_QUALIFIER_CHOICES,
        default='unspecified'
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
    engage_anonymously = models.BooleanField(
        help_text='Whether engage_anonymously or not.',
        default=True,
    )

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


class BanAudit(models.Model):
    user = models.ForeignKey('auth.User', related_name='user_bans')
    banned_by = models.ForeignKey('auth.User', related_name='user_bans_reported')
    banned_on = models.DateTimeField(auto_now=True)
    ban_duration = models.IntegerField()


class Banner(ModelBase):
    TYPE_BANNER = 'banner'
    TYPE_THUMBNAIL = 'thumbnail'
    BANNER_TYPE_CHOICES = (
        (TYPE_BANNER, 'Banner'),
        (TYPE_THUMBNAIL, 'Thumbnail'),
    )
    banner_type = models.CharField(
        max_length=10,
        choices=BANNER_TYPE_CHOICES,
        help_text='Type of vlive module.',
        default=TYPE_BANNER,
    )
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
