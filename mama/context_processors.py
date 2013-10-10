from django.core.cache import cache
from preferences import preferences


def comments_open(request):
    cache_key = "preferences_comments_open"

    context = cache.get(cache_key)
    if not context:
        context = {'comments_open': preferences.SitePreferences.comments_open()}
        cache.set(cache_key, context, 60 * 10)

    return context
