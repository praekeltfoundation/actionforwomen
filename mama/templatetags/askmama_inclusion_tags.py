from copy import copy
from datetime import datetime
from dateutil.relativedelta import *
# import calendar

from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
from django import template
from secretballot.models import Vote


Comment = comments.get_model()
register = template.Library()


@register.inclusion_tag(
    'mama/inclusion_tags/favourite_questions_for_week.html',
    takes_context=True)
def favourite_questions_for_week(context, post, weeks_ago=0):
    context = copy(context)

    # Find the dates for the current week, starting last Sunday and ending next
    # Saturday
    NOW = datetime.now()
    start_sunday = NOW + relativedelta(weekday=SU(-1),
                                       hour=0, minute=0,
                                       second=0, microsecond=0)
    end_saturday = NOW + relativedelta(weekday=SA(+1),
                                       hour=0, minute=0,
                                       second=0, microsecond=0, 
                                       microseconds=-1)
    if weeks_ago > 0:
        start_sunday = start_sunday + relativedelta(weeks=-weeks_ago)
        end_saturday = end_saturday + relativedelta(weeks=-weeks_ago)

    # Filter the questions between the date range
    questions = Comment.objects.filter(submit_date__range=(start_sunday, 
                                                           end_saturday,))

    # Filter the comments linked to the post
    pct = ContentType.objects.get_for_model(post.__class__)
    questions = questions.filter(
        content_type=pct,
        object_pk=post.id)
    questions = questions.exclude(is_removed=True)

    # Work out the vote count for the questions, to sort by the most liked
    # questions, i.e. questions with the most votes. (This is taken from the
    # MostLikedItem view modifier item in jmbo)
    questions = questions.extra(
        select={
            'vote_score': '(SELECT COUNT(*) from %s WHERE vote=1 AND \
object_id=%s.%s AND content_type_id=%s) - (SELECT COUNT(*) from %s WHERE \
vote=-1 AND object_id=%s.%s AND content_type_id=%s)' % (
                Vote._meta.db_table,
                Comment._meta.db_table,
                Comment._meta.pk.attname,
                ContentType.objects.get_for_model(Comment).id,
                Vote._meta.db_table,
                Comment._meta.db_table,
                Comment._meta.pk.attname,
                ContentType.objects.get_for_model(Comment).id
            )
        }
    ).order_by('-vote_score', '-submit_date')

    # leave out replies
    result = [itm for itm in list(questions) \
        if itm.reply_comment_set.count() == 0]

    context['questions'] = result
    context['weeks_ago'] = weeks_ago
    context['week_start'] = start_sunday

    return context
