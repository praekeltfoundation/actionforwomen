from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from django.views.generic import TemplateView

admin.autodiscover()
urlpatterns = patterns('',
    url(
        r'^$',
        TemplateView.as_view(template_name="mama/home.html"),
        name='home'
    ),
    url(
        r'^articles/$',
        TemplateView.as_view(template_name="mama/articles.html"),
        name='articles'
    ),
    
    (r'^', include('jmbo.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
