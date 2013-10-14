import re
import urlparse
from datetime import datetime

from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.comments.views import comments
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

from mama.forms import ContactForm, ProfileForm
from mama.view_modifiers import PopularViewModifier
from mama.models import Banner

from category.models import Category

from poll.forms import PollVoteForm
from poll.models import Poll
from post.models import Post

from preferences import preferences


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

    def get_queryset(self):
        self.category = get_object_or_404(Category, \
                slug__iexact=self.kwargs['category_slug'])
        return Post.permitted.filter(
            Q(primary_category=self.category) | Q(categories=self.category)
        ).distinct()


class CategoryListView(ListView):
    template_name = "post/post_category_list.html"
    paginate_by = 5
    heading_prefix = "More"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['heading_prefix'] = self.heading_prefix
        context['full_heading'] = "%s %s" % (self.heading_prefix, self.category.title)
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

    @method_decorator(cache_page(60 * 60))
    def dispatch(self, *args, **kwargs):
        return super(CategoryListView, self).dispatch(*args, **kwargs)


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


class ProfileView(FormView):
    form_class = ProfileForm
    template_name = "mama/profile.html"

    def form_valid(self, form):
        user = self.request.user
        profile = user.profile
        profile.alias = form.cleaned_data['username']
        profile.delivery_date = form.cleaned_data['delivery_date']
        profile.save()
        messages.success(
            self.request,
            "Thank you! You have successfully been registered. You will be redirected to the homepage shortly."
        )
        return HttpResponseRedirect(reverse('home'))


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
    data["url"] = request.META['HTTP_REFERER']
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
