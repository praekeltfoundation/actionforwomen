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
    context.update({'object_list': [
        Category.objects.get(slug='mama-a-to-z'),
        Category.objects.get(slug='life-guides'),
        Category.objects.get(slug='articles'),
        Category.objects.get(slug='moms-stories'),
    ]})
    return context


@register.inclusion_tag('mama/inclusion_tags/topic_listing.html')
def topic_listing(category_slug, color, more):
    category = Category.objects.get(slug__exact=category_slug)
    object_list = Post.permitted.filter(Q(primary_category=category) | \
            Q(categories=category)).filter(categories__slug='featured')
    return {
        'category': category,
        'object_list': object_list,
        'color': color,
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
def post_listing(context, slug, color):
    context = copy(context)
    category = Category.objects.get(slug__exact=slug)
    object_list = Post.permitted.filter(Q(primary_category=category) | \
            Q(categories=category)).filter(categories__slug='featured')

    context.update({
        'category': category,
        'object_list': object_list,
        'color': color,
    })

    return context
