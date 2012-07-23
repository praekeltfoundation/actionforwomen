import ambient
from category.models import Category
from django.conf import settings
from django.contrib import auth
from django.contrib.comments.views import comments
from django.core.mail import EmailMessage, mail_managers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from mama.forms import ContactForm, PasswordResetForm
from mama.models import UserProfile
from mama.view_modifiers import PopularViewModifier
from poll.forms import PollVoteForm
from poll.models import Poll
from post.models import Post
from preferences import preferences



class CategoryDetailView(DetailView):
    template_name = "post/post_category_detail.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['show_byline'] = self.category.slug not in ['life-guides', 'mama-a-to-z']
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
        return render_to_response('mama/contact_thanks.html', context_instance=RequestContext(self.request))


def logout(request):
    auth.logout(request)
    if 'HTTP_REFERER' in request.META:
        redir_url = request.META['HTTP_REFERER']
    else:
        redir_url = reverse("home")
    return redirect(redir_url)

@csrf_protect
@require_POST
def poll_vote(request, poll_slug):
    poll = get_object_or_404(Poll, slug=poll_slug)
    form = PollVoteForm(request.POST, request=request, poll=poll)
    if form.is_valid():
        form.save()
    
    return redirect(reverse("home"))

@csrf_protect
@require_POST
def post_comment(request, next=None, using=None):
    # Populate dummy data for non required fields
    data = request.POST.copy()
    if not request.user.is_authenticated():
        data["name"] = 'anonymous'
        data["email"] = 'commentor@askmama.mobi'
    data["url"] = 'http://commentor.askmama.mobi'
    request.POST = data
    return comments.post_comment(request, next=request.META['HTTP_REFERER'], using=using)

def server_error(request):
    return HttpResponseServerError(render_to_string('500.html', {
        'STATIC_URL': settings.STATIC_URL
    }))
