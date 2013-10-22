from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from haystack.views import SearchView
from mama.views import (CategoryDetailView, CategoryListView, 
                        ContactView, 
                        ProfileView,
                        AskMamaView, QuestionAnswerView, 
                        MomStoriesListView,
                        MyProfileView, MyProfileEdit, 
                        UpdateDueDateView,
                        PublicProfileView, UserCommentsView,
                        GuidesView, GuidesTopicView, 
                        MoreGuidesView, GuideDetailView)
from mama.forms import PasswordResetForm
import object_tools

admin.autodiscover()
object_tools.autodiscover()


def health(request):
    return HttpResponse('ok')


urlpatterns = patterns('',
    url(r'^health/$', health, name='health'),
    url(
        r'^$',
        TemplateView.as_view(template_name="mama/home.html"),
        name='home'
    ),
    url(
        r'^about/$',
        TemplateView.as_view(template_name="mama/about.html"),
        name='about'
    ),
    url(
        r'^contact/$',
        ContactView.as_view(),
        name='contact'
    ),
    url(
        r'^help/$',
        TemplateView.as_view(template_name="mama/help.html"),
        name='help'
    ),
    url(
        r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'mama/login.html'},
        name='login'
    ),
    url(
        r'^logout/$',
        'mama.views.logout',
        name='logout'
    ),
    url(
        r'^password-reset/$',
        'django.contrib.auth.views.password_reset',
        {
            'password_reset_form': PasswordResetForm,
            'template_name': 'mama/password_reset.html',
        },
        name='password_reset'
    ),
    url(
        r'^password-reset-done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'mama/password_reset_done.html'},
        name='password_reset_done'
    ),
    url(
        r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'mama/password_reset_confirm.html'},
        name='password_reset_confirm'
    ),
    url(
        r'^reset/done/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'mama/password_reset_complete.html'},
        name='password_reset_complete'
    ),
    url(
        r'^poll-vote/(?P<poll_slug>[\w-]+)/$',
        'mama.views.poll_vote',
        name='poll_vote'
    ),
    url(
        r'^post-comment/$',
        'mama.views.post_comment',
        name='post_comment'
    ),
    (r'^comments/', include('django.contrib.comments.urls')),
    url(
        r'^terms/$',
        TemplateView.as_view(template_name="mama/terms.html"),
        name='terms'
    ),
    url(
        r'^ask-mama/$', AskMamaView.as_view(),
        {},
        name='askmama_detail'
    ),
    url(
        r'^ask-mama/answer/(?P<question_id>\d+)/$',
        QuestionAnswerView.as_view(),
        {},
        name='askmama_answer_detail'
    ),
    url(
        r'^moms-stories/list/$',
        MomStoriesListView.as_view(),
        {},
        name='moms_stories_object_list'
    ),
    url(
        r'^guides/list/$',
        GuidesView.as_view(),
        {},
        name='guides_list'
    ),
    url(
        r'^guides/topic/list/(?P<slug>[\w-]+)/$',
        GuidesTopicView.as_view(),
        {},
        name='guides_topic_list'
    ),
    url(
        r'^guides/list/more/$',
        MoreGuidesView.as_view(),
        {},
        name='more_guides_list'
    ),
    url(
        r'^guides/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
        GuideDetailView.as_view(),
        {},
        name='topic_detail'
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
    url(r'^search/', cache_page(SearchView(results_per_page=5), 60 * 60), name='haystack_search'),
    url(
        r'^accounts/register/$', 'registration.views.register',
        {'backend': 'mama.registration_backend.MamaBackend'},
        name='registration_register'
    ),
    url(
        r'^accounts/register/done/',
        login_required(TemplateView.as_view(
            template_name="registration/done.html"
        )),
        name='registration_done'
    ),
    url(
        r'^view/myprofile/$',
        login_required(MyProfileView.as_view()),
        name='view_my_profile'
    ),
    url(
        r'^edit/myprofile/$',
        login_required(MyProfileEdit.as_view()),
        name='edit_my_profile'
    ),
    url(
        r'^accounts/profile/$',
        login_required(ProfileView.as_view()),
        name='profile'
    ),
    url(
        r'^public/profile/(?P<user_id>\d+)/$',
        PublicProfileView.as_view(),
        name='public_profile'
    ),
    url(
        r'^public/usercomments/(?P<user_id>\d+)/$',
        UserCommentsView.as_view(),
        name='public_user_comments'
    ),

    url(
        r'^profile/duedate/$',
        UpdateDueDateView.as_view(),
        name='update_due_date'
    ),

    (r'^survey/', include('survey.urls', namespace='survey')),
    (r'^livechat/', include('livechat.urls', namespace='livechat')),
    (r'^admin/', include(admin.site.urls)),
    (r'^object-tools/', include(object_tools.tools.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
    url(r'^google-credentials/', include('google_credentials.urls')),
    (r'^likes/', include('likes.urls')),
    (r'^yourwords/', include('jmboyourwords.urls')),
    (r'^', include('jmbo.urls')),
)

handler500 = 'mama.views.server_error'

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
