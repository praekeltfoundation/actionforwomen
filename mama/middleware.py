from django.conf import settings
from django.http import HttpResponseNotAllowed


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

            profile = request.user.profile
            if profile.origin != settings.ORIGIN:
                profile.origin = settings.ORIGIN
                profile.save()


class ReadOnlyMiddleware(object):

    ALLOWED_METHODS = frozenset(['GET', 'HEAD'])

    def process_request(self, request):
        if (settings.READ_ONLY_MODE and
                request.method not in self.ALLOWED_METHODS):
            return HttpResponseNotAllowed(self.ALLOWED_METHODS)
