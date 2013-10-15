from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.conf import settings


class TrackOriginMiddleware(object):
    """
    If a request passes through this middleware, the associated user's
    profile will be tagged with `settings.ORIGIN`
    """

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if hasattr(request, 'user'):
            if request.user.is_anonymous():
                return

            try:
                profile = request.user.get_profile()
                if profile.origin != settings.ORIGIN:
                    profile.origin = settings.ORIGIN
                    profile.save()
            except ObjectDoesNotExist:
                pass
