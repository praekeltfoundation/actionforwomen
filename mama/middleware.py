from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


class TrackOriginMiddleware(object):
    """
    If a request passes through this middleware, the associated user's
    profile will be tagged with `settings.ORIGIN`
    """

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")

        profile = request.user.get_profile()
        if profile.origin != settings.ORIGIN:
            profile.origin = settings.ORIGIN
            profile.save()
