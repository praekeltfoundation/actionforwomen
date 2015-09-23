from django.utils.translation import ugettext as _

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

IMAGE_HEADING_STYLE = (
    ('light', 'Light'),
    ('dark', 'Dark'),
)