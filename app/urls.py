from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from haystack.views import SearchView
from haystack.query import SearchQuerySet
from livechat.models import LiveChatResponse
from app.views import (CategoryDetailView, CategoryListView,
                        StoryCommentsView, ConfirmReportView,
                        ContactView,
                        ProfileView, VLiveEditProfile,
                        QuestionAnswerView, MyProfileView, MyProfileEdit,
                        PublicProfileView, UserCommentsView)
from app.forms import PasswordResetForm, PasswordResetEmailForm
from moderator.models import CommentReply
from app.models import Post
from django.contrib.comments import Comment
import object_tools

admin.autodiscover()
object_tools.autodiscover()

postsqs = SearchQuerySet().models(Post)
commentsqs = SearchQuerySet().models(Comment, CommentReply, LiveChatResponse)

def health(request):
    return HttpResponse('ok')


urlpatterns = patterns('',
    url(r'^health/$', health, name='health'),
    url(
        r'^$',
        TemplateView.as_view(template_name="app/home.html"),
        name='home'
    ),
    url(
        r'^about/$',
        TemplateView.as_view(template_name="app/about.html"),
        name='about'
    ),
    url(
        r'^faqs/$',
        TemplateView.as_view(template_name="app/faqs.html"),
        name='faqs'
    ),
    url(
        r'^contact/$',
        ContactView.as_view(),
        name='contact'
    ),
    url(
        r'^feedback/$',
        'app.views.sendfeedback',
        name='feedback'
    ),
    url(
        r'^help/$',
        TemplateView.as_view(template_name="app/help.html"),
        name='help'
    ),
    url(
        r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'app/login.html'},
        name='login'
    ),
    url(
        r'^logout/$',
        'app.views.logout',
        name='logout'
    ),
    url(
        r'^set_lang/$',
        'app.views.set_language',
        name='set_lang'
    ),
    url(
        r'^password-reset/$', 
        'django.contrib.auth.views.password_reset',
        {
            'password_reset_form': PasswordResetEmailForm,
            'template_name': 'app/password_reset_email.html',
        }, 
        name="reset_password_email"
    ),
    url(
        r'^password-reset-done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'app/password_reset_done.html'},
        name='password_reset_done'
    ),
    url(
        r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'app/password_reset_confirm.html'},
        name='password_reset_confirm'
    ),
    url(
        r'^reset/done/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'app/password_reset_complete.html'},
        name='password_reset_complete'
    ),
    url(
        r'^poll-vote/(?P<poll_slug>[\w-]+)/$',
        'app.views.poll_vote',
        name='poll_vote'
    ),
    url(
        r'^post-comment/$',
        'app.views.post_comment',
        name='post_comment'
    ),
    (r'^comments/', include('django.contrib.comments.urls')),
    url(
        r'^terms/$',
        TemplateView.as_view(template_name="app/terms.html"),
        name='terms'
    ),
    url(
        r'^comment-terms/$',
        TemplateView.as_view(template_name="app/includes/comment_terms.html"),
        name='comment-terms'
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
    url(
        r'^content/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/comments/$',
        StoryCommentsView.as_view(),
        {},
        name='story_comments_list'
    ),
    url(r'^search/',  cache_page(SearchView(results_per_page=5,
                                            searchqueryset=postsqs), 60 * 60),
        name='haystack_search'),
    url(
        r'^accounts/register/$', 'registration.views.register',
        {'backend': 'app.registration_backend.MamaBackend'},
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
        r'^comment-agree/$',
        "app.views.agree_comment",
        name='agree_comment'
    ),
    url(
        r'^report-comment/(?P<content_type>[\w-]+)/(?P<id>\d+)/(?P<vote>-?\d+)/$',
        'app.views.report_comment',
        name='report_comment'),
    url(
        r'^confirm-comment-report/(?P<content_type>[\w-]+)/(?P<id>\d+)/$',
        ConfirmReportView.as_view(),
        name='confirm_comment'),

    (r'^survey/', include('survey.urls', namespace='survey')),
    (r'^livechat/', include('livechat.urls', namespace='livechat')),
    (r'^admin/', include(admin.site.urls)),
    (r'^object-tools/', include(object_tools.tools.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
    url(r'^google-credentials/', include('google_credentials.urls')),
    url(r'^likes/like/(?P<content_type>[\w-]+)/(?P<id>\d+)/(?P<vote>-?\d+)$',
        'app.views.like',
        name='like'),
    url(r'^', include('jmbo.urls')),
    url(r'^djga/', include('google_analytics.urls')),
)

handler500 = 'app.views.server_error'

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
