from category.models import Category
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from mama.forms import PasswordResetForm
from mama.models import UserProfile
from mama.view_modifiers import PopularViewModifier
from post.models import Post


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
