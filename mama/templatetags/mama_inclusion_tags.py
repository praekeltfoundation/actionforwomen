from copy import copy
from datetime import datetime

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
    user = context['request'].user
    if user.is_authenticated():
        delivery_date = user.profile.delivery_date
        if delivery_date:
            now = datetime.now().date()
            pre_post = 'pre' if user.profile.is_prenatal() else 'post'
            week = 42 - ((delivery_date - now).days / 7) if user.profile.is_prenatal() else (now - delivery_date).days / 7
        else:
            # Defaults in case user does not have delivery date.
            pre_post = 'pre'
            week = 21
        try:
            category = Category.objects.get(slug="my-pregnancy" if user.profile.is_prenatal() else "my-baby")
            context.update({
                'category': category,
            })
        except Category.DoesNotExist:
            return context

        try:
            week_category = Category.objects.get(slug="%snatal-week-%s" % (pre_post, week))
        except Category.DoesNotExist:
            context.update({
                'object_list': [],
            })
            return context
        object_list = Post.permitted.filter(Q(primary_category=week_category) | \
            Q(categories=week_category)).distinct()
        context.update({
            'object_list': object_list,
        })
    return context


@register.inclusion_tag('mama/inclusion_tags/header.html', takes_context=True)
def header(context):
    context = copy(context)
    help_post = Post.permitted.filter(slug='mama-help')
    if help_post:
        context.update({
            'help_post': help_post[0]
        })
    return context


@register.inclusion_tag('mama/inclusion_tags/topic_listing.html')
def topic_listing(category_slug, more):
    try:
        category = Category.objects.get(slug__exact=category_slug)
    except Category.DoesNotExist:
        return {}
    object_list = Post.permitted.filter(Q(primary_category=category) | \
            Q(categories=category)).filter(categories__slug='featured').distinct()
    return {
        'category': category,
        'object_list': object_list,
        'more': more,
    }


@register.inclusion_tag('mama/inclusion_tags/poll_listing.html', takes_context=True)
def poll_listing(context):
    context = copy(context)
    object_list = Poll.permitted.filter(categories__slug='featured').distinct()

    context.update({
        'object_list': object_list,
    })
    return context


@register.inclusion_tag('mama/inclusion_tags/post_listing.html', \
        takes_context=True)
def post_listing(context, category_slug):
    context = copy(context)
    try:
        category = Category.objects.get(slug__exact=category_slug)
    except Category.DoesNotExist:
        return {}
    object_list = Post.permitted.filter(Q(primary_category=category) | \
            Q(categories=category)).filter(categories__slug='featured').distinct()

    context.update({
        'category': category,
        'object_list': object_list,
    })
    return context


@register.inclusion_tag('mama/inclusion_tags/pagination.html', takes_context=True)
def pagination(context, page_obj):
    context = copy(context)
    context.update({
        'page_obj': page_obj,
        'paginator': getattr(page_obj, 'paginator', None),
    })
    return context


@register.inclusion_tag('mama/inclusion_tags/babycenter_byline.html')
def babycenter_byline(obj):
    if obj.categories.filter(slug='bc-content'):
        return {'display': True}
    else:
        return {}
