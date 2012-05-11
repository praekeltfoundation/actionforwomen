from category.models import Category
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
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
        )


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
        )
        view_modifier = PopularViewModifier(self.request)
        return view_modifier.modify(queryset)
