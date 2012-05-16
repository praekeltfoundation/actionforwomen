from category.models import Category
from django.conf import settings
from django.contrib import auth
from django.core.mail import EmailMessage, mail_managers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from mama.forms import ContactForm, PasswordResetForm
from mama.models import UserProfile
from mama.view_modifiers import PopularViewModifier
from post.models import Post
from preferences import preferences


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

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_queryset(self):
        self.category = get_object_or_404(Category, \
                slug__iexact=self.kwargs['category_slug'])
        queryset = Post.permitted.filter(
            Q(primary_category=self.category) | Q(categories=self.category)
        ).distinct()
        view_modifier = PopularViewModifier(self.request)
        return view_modifier.modify(queryset)


class CategoryListFeaturedView(ListView):
    template_name = "post/post_category_list_featured.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryListFeaturedView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_queryset(self):
        self.category = get_object_or_404(Category, \
                slug__iexact=self.kwargs['category_slug'])
        queryset = Post.permitted.filter(
            Q(primary_category=self.category) | Q(categories=self.category)
        ).filter(categories__slug='featured').distinct()
        return queryset


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


class PasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = "mama/password_reset.html"

    def form_valid(self, form):
        try:
            profile = UserProfile.objects.get(mobile_number__exact=form.cleaned_data['mobile_number'])
            raise NotImplementedError("Implement reset SMS line with throttling.")
            return render_to_response('mama/password_reset_done.html', context_instance=RequestContext(self.request))
        except UserProfile.DoesNotExist:
            form.non_field_errors = "Unable to find an account for the provided mobile number. Please try again." 
            return self.form_invalid(form)


def logout(request):
    auth.logout(request)
    if 'HTTP_REFERER' in request.META:
        redir_url = request.META['HTTP_REFERER']
    else:
        redir_url = reverse("home")
    return redirect(redir_url)


def server_error(request):
    return HttpResponseServerError(render_to_string('500.html', {
        'STATIC_URL': settings.STATIC_URL
    }))
