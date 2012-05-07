from django.db import models
from jmbo.models import ModelBase
from preferences.models import Preferences


class MamaPreferences(Preferences):
    __module__ = 'preferences.models'


class FeaturedContent(ModelBase):
    class Meta:
        proxy=True
