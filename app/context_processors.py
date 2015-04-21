from django.core.cache import cache
from django.conf import settings
from preferences import preferences


def comments_open(request):
    cache_key = "preferences_comments_open"

    context = cache.get(cache_key)
    if not context:
        context = {'comments_open': preferences.SitePreferences.comments_open()}
        cache.set(cache_key, context, 60 * 10)

    return context


def read_only_mode(request):
    return {
        'READ_ONLY_MODE': settings.READ_ONLY_MODE
    }
