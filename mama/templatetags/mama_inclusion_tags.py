from copy import copy
from category.models import Category
from django import template
from django.db.models import Q
from poll.models import Poll
from post.models import Post

register = template.Library()


@register.inclusion_tag('mama/inclusion_tags/ages_and_stages.html', \
        takes_context=True)
def ages_and_stages(context):
    context = copy(context)
    return context


@register.inclusion_tag('mama/inclusion_tags/header.html', takes_context=True)
def header(context):
    context = copy(context)
    context['object_list'] = []
    for category_slug in ['mama-a-to-z', 'life-guides', 'articles', 'moms-stories']:
        try:
            context['object_list'].append(Category.objects.get(slug=category_slug))
        except Category.DoesNotExist:
            pass
    return context


@register.inclusion_tag('mama/inclusion_tags/topic_listing.html')
def topic_listing(category_slug, more):
    try:
        category = Category.objects.get(slug__exact=category_slug)
    except Category.DoesNotExist:
        return {}
    object_list = Post.permitted.filter(Q(primary_category=category) | \
            Q(categories=category)).filter(categories__slug='featured')
    return {
        'category': category,
        'object_list': object_list,
        'more': more,
    }


@register.inclusion_tag('mama/inclusion_tags/poll_listing.html')
def poll_listing():
    object_list = Poll.permitted.filter(categories__slug='featured')

    return {
        'object_list': object_list,
    }


@register.inclusion_tag('mama/inclusion_tags/post_listing.html', \
        takes_context=True)
def post_listing(context, category_slug):
    context = copy(context)
    try:
        category = Category.objects.get(slug__exact=category_slug)
    except Category.DoesNotExist:
        return {}
    object_list = Post.permitted.filter(Q(primary_category=category) | \
            Q(categories=category)).filter(categories__slug='featured')

    context.update({
        'category': category,
        'object_list': object_list,
    })
    return context
