from copy import copy
from datetime import datetime
from dateutil.relativedelta import *
from mama.utils import askmama_can_vote
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
from django import template
from django.core.paginator import Paginator

from secretballot.models import Vote


Comment = comments.get_model()
register = template.Library()


@register.inclusion_tag(
    'mama/inclusion_tags/favourite_questions_for_week.html',
    takes_context=True)
def favourite_questions_for_week(context, post, 
                                 weeks_ago=0, cpage=1, sort='pop'):
    """
    This template tag displays the questions for a given week on the AskMAMA
    section of the site. Week could be 0, 1 or 2. 0 is the current week, 1 is
    the previous week, and 2 is everything older than 1 week.

    Questions are simply comments linked to the lead in post (latest pinned
    post) for the "Ask MAMA" category.

    The moderator's CommentReply constitutes the expert's reply to a question.
    """
    context = copy(context)

    # Find the dates for the current week, starting last Friday and ending
    # next Thursday
    can_vote, end_thursday, start_friday = askmama_can_vote(weeks_ago, datetime.now())


    # Subtract the amount of weeks in the past.
    if weeks_ago > 0:
        start_friday = start_friday + relativedelta(weeks=-weeks_ago)
        end_thursday = end_thursday + relativedelta(weeks=-weeks_ago)

    if weeks_ago < 2:
        # Filter the questions between the date range
        questions = Comment.objects.filter(submit_date__range=(start_friday, 
                                                               end_thursday,))
    else:
        # Filter all the older questions.
        questions = Comment.objects.filter(submit_date__lt=(end_thursday)) 



    # Filter the comments linked to the post
    pct = ContentType.objects.get_for_model(post.__class__)
    questions = questions.filter(
        content_type=pct,
        object_pk=post.id)
    questions = questions.exclude(is_removed=True)

    # leave out the moderator answers
    questions = questions.exclude(user__is_staff=True)

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
    )
    
    # apply the sort order. 'pop' is the default.
    if sort == 'pop':
        questions = questions.order_by('-vote_score', '-submit_date')
    elif sort == 'date':
        questions = questions.order_by('-submit_date')
    elif sort == 'alph':
        questions = questions.order_by('comment')
    else:
        questions = questions.order_by('-vote_score', '-submit_date')

    # if we are viewing last week' and older sessions, only show the top 10
    if weeks_ago > 0:
        questions = questions[:10]

    # return the results paginated.
    paginator = Paginator(questions, 15)
    comments_page = paginator.page(cpage)

    # check if we can comment. we need to be authenticated, at least
    can_comment, code = post.can_comment(context['request'])
    context.update({
        'can_render_comment_form': can_comment,
        'can_comment_code': code
        })

    context['cpage'] = cpage
    context['sort'] = sort
    context['questions'] = comments_page
    context['weeks_ago'] = weeks_ago
    context['week_start'] = start_friday
    context['week_end'] = end_thursday
    context['can_vote'] = can_vote

    return context
