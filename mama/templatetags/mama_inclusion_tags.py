from copy import copy
from datetime import datetime
try:
  from random import SystemRandom
  random = SystemRandom()
except:
  import random

from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template import Context, Template

from category.models import Category
from poll.models import Poll
from post.models import Post


register = template.Library()


@register.inclusion_tag('mama/inclusion_tags/ages_and_stages.html',
                        takes_context=True)
def ages_and_stages(context):
    context = copy(context)
    user = context['request'].user
    if user.is_authenticated():
        profile = user.profile
        context.update({'profile': profile})
        delivery_date = profile.delivery_date
        if delivery_date:
            now = datetime.now().date()
            pre_post = 'pre' if profile.is_prenatal() else 'post'
            week = 42 - ((delivery_date - now).days / 7) if profile.is_prenatal() else (now - delivery_date).days / 7
        else:
            # Defaults in case user does not have delivery date.
            pre_post = 'pre'
            week = 21
        try:
            category = Category.objects.get(slug="my-pregnancy" if profile.is_prenatal() else "my-baby")
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
        object_list = Post.permitted.filter(Q(primary_category=week_category) |
                                            Q(categories=week_category)).distinct()
        context.update({
            'object_list': object_list,
        })
    return context


@register.inclusion_tag('mama/inclusion_tags/page_header.html', takes_context=True)
def page_header(context):
    context = copy(context)
    help_post = Post.permitted.filter(slug='mama-help')
    if help_post:
        context.update({
            'help_post': help_post[0],
        })
    return context


@register.inclusion_tag(
    'mama/inclusion_tags/registration_banner.html',
    takes_context=True)
def registration_banner(context):
    context = copy(context)
    return context


@register.inclusion_tag(
    'mama/inclusion_tags/askmama_banner.html',
    takes_context=True)
def askmama_banner(context):
    context = copy(context)
    return context


@ register.inclusion_tag(
    'mama/inclusion_tags/random_guide_banner.html',
    takes_context=True)
def random_guide_banner(context):
    context = copy(context)

    # get the published, featured guides
    qs = Post.permitted.filter(
            primary_category__slug='life-guides',
            categories__slug='featured')

    # select a guide at random
    try:
        random_guide = random.choice(qs)
        context.update({
            'random_guide': {
                'title': random_guide.title,
                'description': random_guide.description,
                'url': random_guide.get_absolute_category_url()
            }
        })
    except IndexError:
        pass

    return context


@register.inclusion_tag('mama/inclusion_tags/page_header.html', takes_context=True)
def pml_page_header(context):
    context = copy(context)
    help_post = Post.permitted.filter(slug='mama-help')
    links = [
        {
            'title': 'Home',
            'url': reverse('home'),
        },
        {
            'title': 'A-to-Z',
            'url': reverse('category_object_list', kwargs={'category_slug': 'mama-a-to-z'}),
        },
        {
            'title': 'Life Guides',
            'url': reverse('category_object_list', kwargs={'category_slug': 'life-guides'}),
        },
        {
            'title': 'Articles',
            'url': reverse('category_object_list', kwargs={'category_slug': 'articles'}),
        },
        {
            'title': "Moms' Stories",
            'url': reverse('category_object_list', kwargs={'category_slug': 'moms-stories'}),
        }
    ]
    if help_post:
        links.append(
            {
                'title': 'Help',
                'url': help_post[0].get_absolute_category_url(),
            }
        )
    context['links'] = links
    return context


@register.inclusion_tag('mama/inclusion_tags/topic_listing.html', takes_context=True)
def topic_listing(context, category_slug, more):
    context = copy(context)
    try:
        category = Category.objects.get(slug__exact=category_slug)
    except Category.DoesNotExist:
        return {}
    object_list = Post.permitted.filter(
        Q(primary_category=category) |
        Q(categories=category)
    ).filter(categories__slug='featured').distinct()
    context.update({
        'category': category,
        'object_list': object_list,
        'full_heading': "More %s" % category.title if more else category.title
    })
    return context


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
    result = _get_content_object_list(context, category_slug)
    result['object_list'] = result['object_list'][:2]
    return result


@register.inclusion_tag('mama/inclusion_tags/stories_listing.html',
        takes_context=True)
def stories_listing(context, category_slug):
    result = _get_content_object_list(context, category_slug)
    result['object_list'] = result['object_list'][:3]
    return result


def _get_content_object_list(ctx_dict, category_slug):
    ctx_dict = copy(ctx_dict)
    try:
        category = Category.objects.get(slug__exact=category_slug)
    except Category.DoesNotExist:
        return ctx_dict
    object_list = Post.permitted.filter(Q(primary_category=category) | \
            Q(categories=category))
    object_list = object_list.filter(categories__slug='featured').distinct()

    ctx_dict.update({
        'category': category,
        'object_list': object_list,
    })
    return ctx_dict


@register.inclusion_tag('mama/inclusion_tags/pagination.html', takes_context=True)
def pagination(context, page_obj):
    context = copy(context)
    context.update({
        'page_obj': page_obj,
        'paginator': getattr(page_obj, 'paginator', None),
    })

    pages = []
    for page in page_obj.paginator.page_range:
        pages.append({
            'number': page ,
            'url': Template("{% load jmbo_template_tags %}{% smart_query_string 'page' " + str(page) + " %}").render(Context(context))
        })
    page_number = page_obj.number - 1
    if page_number < 3:
        slice_start = 0
    else:
        slice_start = page_number - 2
    if page_number + 2 >= len(pages):
        slice_start = len(pages) - 5
    context['pages'] = pages[slice_start: slice_start + 5]
    if page_obj.has_previous():
        context['previous_url'] = Template("{% load jmbo_template_tags %}{% smart_query_string 'page' page_obj.previous_page_number %}").render(Context(context))
    if page_obj.has_next():
        context['next_url'] = Template("{% load jmbo_template_tags %}{% smart_query_string 'page' page_obj.next_page_number %}").render(Context(context))

    return context


@register.inclusion_tag('mama/inclusion_tags/babycenter_byline.html')
def babycenter_byline(obj):
    if obj.categories.filter(slug='bc-content'):
        return {'display': True}
    else:
        return {}



@register.inclusion_tag('mama/inclusion_tags/vlive_object_comments.html', takes_context=True)
def vlive_object_comments(context, obj):
    def can_comment(obj, request):
        """
        Determine if user can comment.
        We don't use ModelBase.can_comment since that unnecessarily traverses to base.
        """
        # can't comment if commenting is closed
        if obj.comments_closed:
            return False

        # can't comment if commenting is disabled
        if not obj.comments_enabled:
            return False

        # anonymous users can't comment if anonymous comments are disabled
        if not request.user.is_authenticated() and not \
                obj.anonymous_comments:
            return False

        # can't comment if user is banned
        if request.user.is_authenticated() and request.user.profile.banned:
            return False

        return True

    def get_paginated_comments(obj, request):
        from django.contrib.comments.models import Comment
        from django.contrib.contenttypes.models import ContentType
        ctype = ContentType.objects.get_for_model(obj)
        comments = list(Comment.objects.filter(
            content_type=ctype,
            object_pk=obj.pk,
            is_public=True,
            is_removed=False
        ).select_related('user').order_by('-submit_date'))

        paginator = Paginator(comments, 5)
        page = request.GET.get('page')

        try:
            page_comments = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page_comments = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page_comments = paginator.page(paginator.num_pages)

        return page_comments, len(comments)

    request = context['request']
    comments, count = get_paginated_comments(obj, request)
    context.update({
        'object': obj,
        'page_comments': comments,
        'comment_count': count,
        'can_render_comment_form': can_comment(obj, request),
    })

    return context
