from django.conf import settings
from django.core.urlresolvers import reverse


class PMLMiddleware(object):
    """
    Sets response mimetype to text/xml.
    """
    def process_response(self, request, response):
        # When developing on error show trace page
        if settings.DEBUG and response.status_code in [500, ]:
            return response

        # Don't apply xml to admin views.
        if request.path.startswith(reverse('admin:index')):
            return response

        # Ste xml content type for everything else.
        response['Content-Type'] = 'text/xml'
        return response


class PMLFormMiddleware(object):
    def process_request(self, request):
        if request.GET.get('submit'):
            request.method = "POST"
            request.POST = request.GET
