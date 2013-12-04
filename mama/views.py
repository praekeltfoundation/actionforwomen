import re
import urlparse
from datetime import datetime
from dateutil import parser

from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.comments.views import comments
from django.contrib.comments import get_model
from django.core.mail import EmailMessage, mail_managers
from django.core.urlresolvers import reverse
from django.db.models import Q, F
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from mama.forms import (
    ContactForm,
    DueDateForm,
    MxitDueDateForm,
    ProfileForm,
    VLiveProfileEditForm,
    EditProfileForm
)
from mama.view_modifiers import PopularViewModifier
from mama.models import Banner, DefaultAvatar

from category.models import Category

from poll.forms import PollVoteForm
from poll.models import Poll
from post.models import Post

from mama.constants import (
    RELATION_PARENT_CHOICES, 
    RELATION_PARENT_TO_BE_CHOICES 
)

from preferences import preferences


Comment = get_model()


URL_REGEX = re.compile(
    r'(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)', re.IGNORECASE
)


class CategoryDetailView(DetailView):
    template_name = "post/post_category_detail.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_object(self):
        post = Post.permitted.get(slug=self.kwargs['slug'])
        self.category = post.primary_category
        return post


class CategoryListView(ListView):
    template_name = "post/post_category_list.html"
    paginate_by = 10
    heading_prefix = ""

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['heading_prefix'] = self.heading_prefix
        context['full_heading'] = "%s %s" % (
            self.heading_prefix, self.category.title)
        return context

    def get_queryset(self):
        self.category = get_object_or_404(Category, \
                slug__iexact=self.kwargs['category_slug'])
        queryset = Post.permitted.filter(
            Q(primary_category=self.category) | Q(categories=self.category)
        ).exclude(categories__slug='featured').distinct()
        view_modifier = PopularViewModifier(self.request)
        active_modifiers = view_modifier.get_active_items()
        if active_modifiers:
            self.heading_prefix = active_modifiers[0].title
        return view_modifier.modify(queryset)

    # @method_decorator(cache_page(60 * 60))
    # def dispatch(self, *args, **kwargs):
    #     return super(CategoryListView, self).dispatch(*args, **kwargs)


class GuidesView(TemplateView):
    """
    """
    template_name="mama/guides.html"

    def get_context_data(self, **kwargs):
        context = super(GuidesView, self).get_context_data(**kwargs)

        # Collect the relevant categories
        featured = self._get_category('featured')
        mama_a2z = self._get_category('mama-a-to-z')
        life_guides = self._get_category('life-guides')
        context['category'] = life_guides

        # Get the stage guides featured articles
        if featured and mama_a2z:
            qs = Post.permitted.filter(
                primary_category=mama_a2z, 
                categories=featured)
            stages_leaders = [{
                'title': item.title,
                'slug': item.slug
            } for item in qs]
            context['stages_leaders'] = stages_leaders

        # Get the life guides featured articles
        if featured and life_guides:
            qs = Post.permitted.filter(
                primary_category=life_guides, 
                categories=featured)
            life_guide_leaders = [{
                'title': item.title,
                'slug': item.slug
            } for item in qs]
            context['life_guide_leaders'] = life_guide_leaders

        return context

    def _get_category(self, slug):
        try:
            category = Category.objects.get(slug=slug)
            return category
        except Category.DoesNotExist:
            return None


class GuidesTopicView(DetailView):
    """ List the guide topices in a specific 'category'
    """
    template_name = 'mama/guide_topic_list.html'
    
    def get_object(self):
        post = Post.permitted.get(slug=self.kwargs['slug'])
        self.category = post.primary_category
        return post

    def get_context_data(self, **kwargs):
        context = super(GuidesTopicView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class MoreGuidesView(CategoryListView):
    template_name="mama/more_guides.html"
    paginate_by = 10
    heading_prefix = "More"

    def get_context_data(self, **kwargs):
        context = super(MoreGuidesView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['sort'] = self.request.GET.get('sort','pop')
        context['page'] = self.request.GET.get('page','1')
        return context

    def get_queryset(self):
        """ Only return Post's that are of category "life-guides".
        """
        self.category = get_object_or_404(
            Category,
            slug__iexact='life-guides')
        queryset = Post.permitted.filter(
            Q(primary_category__slug__in=('life-guides', 'mama-a-to-z',)) | \
            Q(categories__slug__in=('life-guides', 'mama-a-to-z',))
        ).exclude(categories__slug__in=('featured',)).distinct()

        sort = self.request.GET.get('sort','pop')
        if sort == 'pop':
            view_modifier = PopularViewModifier(self.request)
            active_modifiers = view_modifier.get_active_items()
            if active_modifiers:
                self.heading_prefix = active_modifiers[0].title
            return view_modifier.modify(queryset)
        elif sort == 'date':
            return queryset.order_by('-created')
        elif sort == 'alph':
            return queryset.order_by('title')
        return queryset


class GuideDetailView(CategoryDetailView):
    template_name = "mama/topic_detail.html"


class MomStoriesListView(CategoryListView):
    template_name = "mama/moms-stories.html"
    paginate_by = 10
    heading_prefix = "More"

    def get_queryset(self):
        """ Only return Post's that are of category "moms-stories".
        """
        self.category = get_object_or_404(
            Category,
            slug__iexact='moms-stories')
        queryset = Post.permitted.filter(
            Q(primary_category=self.category) | \
            Q(categories=self.category)
        ).exclude(categories__slug__in=('featured',)).distinct()
        view_modifier = PopularViewModifier(self.request)
        active_modifiers = view_modifier.get_active_items()
        if active_modifiers:
            self.heading_prefix = active_modifiers[0].title
        return view_modifier.modify(queryset)


class AskMamaView(CategoryDetailView):
    """
    This view surfaces the AskMAMA section of the site. It is subclassing
    CategoryDetailView, 
    """

    template_name = "mama/askmama.html"
    heading_prefix = ""
    context_object_name = 'lead_in_post'

    def get_context_data(self, **kwargs):
        context = super(AskMamaView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['weeks_ago'] = int(self.request.GET.get('wk', '0'))
        context['cpage'] = int(self.request.GET.get('page', '1'))
        context['sort'] = self.request.GET.get('sort','pop')
        return context

    def get_object(self, queryset=None):
        """ 
        This is the Post that explains what the AskMAMA section is all about
        and that all the questions and answer comments will be hanging off, to
        enable use the likes and moderation functionality.

        We return the latest pinned post in this category. Ideally, you should
        create only one pinned Post in the category, and just change the
        content if you want to. If you create new pinned Posts, the comments
        linked to the older article will not be shown.
        """
        self.category = get_object_or_404(Category,
                                          slug__iexact='ask-mama')
        try:
            return Post.permitted.filter(
                pin__category=self.category
            ).latest('created')
        except Post.DoesNotExist:
            return None


class QuestionAnswerView(TemplateView):
    """ This view displays a question and its answer in the AskMAMA section.
    """
    template_name = "mama/question_and_answer.html"

    def get_context_data(self, **kwargs):
        """ Retrieve the question and its answer
        """
        context = super(QuestionAnswerView, self).get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category,
                                          slug__iexact='ask-mama')
        question_id = kwargs.get('question_id', None)
        question = Comment.objects.get(pk=question_id)
        context['question'] = question
        context['answers'] = question.replied_to_comment_set.all()
        return context


class ContactView(FormView):
    form_class = ContactForm
    template_name = "mama/contact.html"

    def form_valid(self, form):
        recipients = [recipient.email for recipient in \
                preferences.SitePreferences.contact_email_recipients.all()]
        mobile_number = form.cleaned_data['mobile_number']
        message = "Mobile Number: \n%s\n\nMessage: \n%s" % (mobile_number, form.cleaned_data['message'])

        if not recipients:
            mail_managers(
                'Error: No contact recipients specified',
                "A user is trying to contact MAMA but no contact email recipients could be found.\n\nUser's Message:\n\n%s" % message,
                fail_silently=False
            )

        else:
            subject = "Contact Message from MAMA user"
            from_address = "MAMA <contact@askmama.mobi>"
            mail = EmailMessage(
                subject,
                message,
                from_address,
                recipients,
                headers={'From': from_address, 'Reply-To': from_address}
            )
            mail.send(fail_silently=False)

        # TODO: This should be a redirect to prevent a double POST ???
        return render_to_response('mama/contact_thanks.html', context_instance=RequestContext(self.request))


class MyProfileView(TemplateView):
    """
    Enables viewing of the user's profile in the HTML site, by the profile
    owner.
    """
    template_name = 'mama/viewprofile.html'

    def get_context_data(self, **kwargs):
        """ Retrieve the user profile
        """
        context = super(MyProfileView, self).get_context_data(**kwargs)
        user = self.request.user
        profile = user.profile
        context['username'] = user.username
        if profile.avatar:
            context['avatar'] = profile.avatar.url
        context['mobile_number'] = profile.mobile_number
        context['relation_description'] = profile.relation_description()
        context['about_me'] = profile.about_me
        context['baby_name'] = profile.baby_name
        context['date_type'] = profile.date_qualifier
        context['unknown_due_date'] = profile.unknown_date
        context['date_description'] = profile.get_date_qualifier_display
        context['delivery_date'] = profile.delivery_date
        return context


class PublicProfileView(TemplateView):
    """
    This is the public view of a member's profile.
    """
    template_name = 'mama/public_profile_view.html'

    def get_context_data(self, **kwargs):
        context = super(PublicProfileView, self).get_context_data(**kwargs)
        user = auth.models.User.objects.get(pk=kwargs['user_id'])
        profile = user.profile
        context['user_id'] = user.id
        context['alias'] = profile.alias if profile.alias else 'Anon.'
        if profile.avatar:
            context['avatar'] = profile.avatar.url
        context['mobile_number'] = profile.mobile_number
        context['comments'] = user.comment_comments.all().count()
        context['relation_description'] = profile.relation_description()
        context['about_me'] = profile.about_me
        context['baby_name'] = profile.baby_name
        context['date_type'] = profile.date_qualifier
        context['unknown_due_date'] = profile.unknown_date
        context['date_description'] = profile.get_date_qualifier_display
        context['delivery_date'] = profile.delivery_date
        return context


class UserCommentsView(ListView):
    """
    Shows a list of the user's comments
    """
    template_name = 'mama/public_comments_view.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        """
        Add information to the context
        """
        context = super(UserCommentsView, self).get_context_data(**kwargs)
        user = auth.models.User.objects.get(pk=self.kwargs['user_id'])
        context['comment_maker'] = user
        return context

    def get_queryset(self):
        """ return the comments for the user
        """
        user = auth.models.User.objects.get(pk=self.kwargs['user_id'])
        return user.comment_comments.all()


class MyProfileEdit(FormView):
    """
    Enables editing of the user's profile in the HTML site
    """
    form_class = EditProfileForm
    template_name = 'mama/editprofile.html'

    def get_initial(self):
        initial = self.initial.copy()
        user = self.request.user
        profile = user.profile
        initial['username'] = user.username
        initial['avatar'] = profile.avatar
        initial['mobile_number'] = profile.mobile_number
        initial['relation_to_baby'] = profile.relation_to_baby
        initial['about_me'] = profile.about_me
        initial['baby_name'] = profile.baby_name
        if profile.date_qualifier == 'unspecified':
            if profile.delivery_date is not None:
                if profile.delivery_date < datetime.now().date():
                    initial['date_qualifier'] = 'birth_date'
                else:
                    initial['date_qualifier'] = 'due_date'
            else:
                initial['date_qualifier'] = 'due_date'
        else:
            initial['date_qualifier'] = profile.date_qualifier
        initial['unknown_date'] = profile.unknown_date
        initial['delivery_date'] = profile.delivery_date
        initial['baby_has_been_born'] = profile.date_qualifier == 'birth_date'
        return initial

    def get_form(self, form_class):
        form = super(MyProfileEdit, self).get_form(form_class)
        if form.initial['date_qualifier'] == 'due_date':
            form.fields['relation_to_baby'].choices = RELATION_PARENT_TO_BE_CHOICES
            form.fields['delivery_date'].label = 'Due Date'
        else:
            form.fields['relation_to_baby'].choices = RELATION_PARENT_CHOICES
            form.fields['delivery_date'].label = 'Birth Date'
            del form.fields['unknown_date']
            del form.fields['baby_has_been_born']
        return form

    def form_valid(self, form):
        """
        Collect and save the updated profile information and redirect to the
        user's profile page.

        If she indicated that the baby has been born, update the date qualifier
        and the unknown date values.
        """
        user = self.request.user
        profile = user.profile
        profile.alias = form.cleaned_data['username']
        profile.mobile_number = form.cleaned_data['mobile_number']
        profile.relation_to_baby = form.cleaned_data['relation_to_baby']
        profile.about_me = form.cleaned_data['about_me']
        profile.baby_name = form.cleaned_data['baby_name']
        profile.date_qualifier = form.cleaned_data['date_qualifier']
        try:
            profile.unknown_date = form.cleaned_data['unknown_date']
        except KeyError:
            pass
        try:
            if form.cleaned_data['baby_has_been_born']:
                profile.date_qualifier = 'birth_date'
                profile.unknown_date = False
        except KeyError:
            pass
        profile.delivery_date = form.cleaned_data['delivery_date']

        # save the avatar from the raw form data
        if form.data.has_key('default_avatar_id'):
            obj = DefaultAvatar.objects.get(
                id=int(form.data['default_avatar_id'])
            )
            profile.avatar = obj.image

        profile.save()
        return HttpResponseRedirect(reverse('view_my_profile'))


class UpdateDueDateView(FormView):
    form_class = DueDateForm
    template_name = 'mama/update_due_date.html'

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        user = self.request.user
        profile = user.profile
        profile.delivery_date = form.cleaned_data['due_date']
        profile.date_qualifier = 'due_date'
        profile.unknown_date = False
        profile.save()
        return super(UpdateDueDateView, self).form_valid(form)


class MxitUpdateDueDateView(FormView):
    form_class = MxitDueDateForm
    template_name = 'mama/update_due_date.html'

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        user = self.request.user
        profile = user.profile
        profile.delivery_date = form.cleaned_data['due_date']
        profile.date_qualifier = 'due_date'
        profile.unknown_date = False
        profile.save()
        return super(MxitUpdateDueDateView, self).form_valid(form)


class ProfileView(FormView):
    """
    This seems to be the registration form view specifically for VLive
    """
    form_class = ProfileForm
    template_name = "mama/profile.html"

    def form_valid(self, form):
        user = self.request.user
        profile = user.profile
        profile.alias = form.cleaned_data['username']
        if form.cleaned_data['delivery_date']:
            # parser returns today's date for an empty string.
            profile.delivery_date = parser.parse(
                form.cleaned_data['delivery_date'])
        profile.save()
        messages.success(
            self.request,
            "Thank you! You have successfully been registered. You will be redirected to the homepage shortly."
        )
        return HttpResponseRedirect(reverse('home'))


class VLiveEditProfile(FormView):
    """
    The profile edit form view specifically for VLive
    """
    form_class = VLiveProfileEditForm
    template_name = "mama/editprofile.html"

    def get_initial(self):
        initial = self.initial.copy()
        user = self.request.user
        profile = user.profile
        initial['username'] = profile.alias
        initial['relation_to_baby'] = profile.relation_to_baby
        initial['about_me'] = profile.about_me
        initial['baby_name'] = profile.baby_name
        if profile.date_qualifier == 'unspecified':
            if profile.delivery_date is not None:
                if profile.delivery_date < datetime.now().date():
                    initial['date_qualifier'] = 'birth_date'
                else:
                    initial['date_qualifier'] = 'due_date'
            else:
                initial['date_qualifier'] = 'due_date'
        else:
            initial['date_qualifier'] = profile.date_qualifier
        initial['unknown_date'] = profile.unknown_date
        initial['delivery_date'] = profile.delivery_date
        initial['baby_has_been_born'] = profile.date_qualifier == 'birth_date'
        return initial

    def get_form(self, form_class):
        form = super(VLiveEditProfile, self).get_form(form_class)
        if form.initial['date_qualifier'] == 'due_date':
            form.fields['relation_to_baby'].choices = RELATION_PARENT_TO_BE_CHOICES
            form.fields['delivery_date'].label = 'Due Date'
        else:
            form.fields['relation_to_baby'].choices = RELATION_PARENT_CHOICES
            form.fields['delivery_date'].label = 'Birth Date'
            del form.fields['unknown_date']
            del form.fields['baby_has_been_born']
        return form

    def form_valid(self, form):
        """
        Collect and save the updated profile information and redirect to the
        user's profile page.

        If she indicated that the baby has been born, update the date qualifier
        and the unknown date values.
        """
        user = self.request.user
        profile = user.profile
        profile.alias = form.cleaned_data['username']
        profile.relation_to_baby = form.cleaned_data['relation_to_baby']
        profile.about_me = form.cleaned_data['about_me']
        profile.baby_name = form.cleaned_data['baby_name']
        profile.date_qualifier = form.cleaned_data['date_qualifier']
        try:
            profile.unknown_date = form.cleaned_data['unknown_date']
        except KeyError:
            pass
        try:
            if form.cleaned_data['baby_has_been_born']:
                profile.date_qualifier = 'birth_date'
                profile.unknown_date = False
        except KeyError:
            pass
        if form.cleaned_data['delivery_date']:
            profile.delivery_date = parser.parse(
                form.cleaned_data['delivery_date'])

        # save the avatar from the raw form data
        if form.data.has_key('default_avatar_id'):
            obj = DefaultAvatar.objects.get(
                id=int(form.data['default_avatar_id'])
            )
            profile.avatar = obj.image

        profile.save()
        return HttpResponseRedirect(reverse('view_my_profile'))


class BannerView(TemplateView):
    template_name = "pml/carousel.xml"

    def get_context_data(self, **kwargs):
        context = super(BannerView, self).get_context_data(**kwargs)
        now = datetime.now().time()

        banners = Banner.permitted.filter(
                    # in between on & off
                    Q(time_on__lte=now, time_off__gte=now) |
                    # roll over night, after on, before 24:00
                    Q(time_on__lte=now, time_off__lte=F('time_on')) |
                    # roll over night, before off, after 24:00
                    Q(time_off__gte=now, time_off__lte=F('time_on')) |
                    # either time on or time of not specified.
                    Q(time_on__isnull=True) | Q(time_off__isnull=True)
                ).order_by('?')

        context.update({
            'banner': banners[0] if banners.exists() else None,
            'ROOT_URL': settings.ROOT_URL,
        })
        return context


def logout(request):
    auth.logout(request)
    # if 'HTTP_REFERER' in request.META:
    #     redir_url = request.META['HTTP_REFERER']
    # else:
    #     redir_url = reverse("home")
    # return redirect(redir_url)
    return redirect(reverse("home"))


@csrf_protect
@require_POST
def poll_vote(request, poll_slug):
    poll = get_object_or_404(Poll, slug=poll_slug)
    form = PollVoteForm(request.POST, request=request, poll=poll)
    if form.is_valid():
        form.save()
    else:
        messages.success(
            request,
            "Please select an option before voting."
        )

    return redirect(reverse("home"))


@csrf_protect
@require_POST
def post_comment(request, next=None, using=None):
    # Populate dummy data for non required fields
    data = request.POST.copy()

    # Resolve comment name from profile alias, username, or anonymous.
    data["name"] = 'anonymous'
    if request.user.is_authenticated():
        profile = request.user.profile
        if profile.alias:
            data['name'] = profile.alias

    data["email"] = 'commentor@askmama.mobi'
    data["url"] = request.META.get('HTTP_REFERER', None)

    # For mxit, we add a next field to the comment form
    if not data["url"] and data.get("next", None):
        data["url"] = data["next"]

    request.POST = data

    # Reject comments if commenting is closed
    if not preferences.SitePreferences.comments_open():
        return comments.CommentPostBadRequest("Comments are closed.")

    # Ignore comments containing URLs
    if re.search(URL_REGEX, data['comment']):
        return comments.CommentPostBadRequest("URLs are not allowed.")

    # Set the host header to the same as refering host, thus preventing PML
    # tunnel tripping up django.http.utils.is_safe_url.
    request.META['HTTP_HOST'] = urlparse.urlparse(data['url'])[1]

    return comments.post_comment(
        request,
        next=data["url"],
        using=using
    )


def server_error(request):
    return HttpResponseServerError(render_to_string('500.html', {
        'STATIC_URL': settings.STATIC_URL
    }))
