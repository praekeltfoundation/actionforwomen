from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from mama.views import CategoryDetailView, CategoryListView

admin.autodiscover()
urlpatterns = patterns('',
    url(
        r'^$',
        TemplateView.as_view(template_name="mama/home.html"),
        name='home'
    ),
    url(
        r'^about$',
        TemplateView.as_view(template_name="mama/about.html"),
        name='about'
    ),
    url(
        r'^contact$',
        TemplateView.as_view(template_name="mama/contact.html"),
        name='contact'
    ),
    url(
        r'^help$',
        TemplateView.as_view(template_name="mama/help.html"),
        name='help'
    ),
    url(
        r'^terms$',
        TemplateView.as_view(template_name="mama/terms.html"),
        name='terms'
    ),
    url(
        r'^content/(?P<category_slug>[\w-]+)/list/$',
        CategoryListView.as_view(),
        {},
        name='category_object_list'
    ),
    url(
        r'^content/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
        CategoryDetailView.as_view(),
        {},
        name='category_object_detail'
    ),
    (r'^accounts/', include('userprofile.backends.simple.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^', include('jmbo.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
