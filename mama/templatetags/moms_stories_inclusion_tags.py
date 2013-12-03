from copy import copy

from django import template
from django.db.models import Q
from django.template import Context, Template
from django.contrib.sites.models import Site

from category.models import Category
from jmboyourwords.models import YourStoryCompetition


register = template.Library()


@register.inclusion_tag('mama/inclusion_tags/story_competition.html',
                        takes_context=True)
def your_story_competition(context):
    """ Display the latest available your story competition.
    """
    context = copy(context)
    qs = YourStoryCompetition.objects.filter(published=True)
    qs = qs.filter(sites=Site.objects.get_current())
    qs = qs.order_by('-publish_on')
    try:
        context['your_story_competition'] = qs.latest('publish_on')
    except YourStoryCompetition.DoesNotExist:
        pass
    import pdb;pdb.set_trace()
    return context
