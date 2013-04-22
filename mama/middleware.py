class PMLMiddleware(object):
    """
    Sets response mimetype to text/xml.
    """
    def process_response(self, request, response):
        response['Content-Type'] = 'text/xml'
        return response


class PMLFormMiddleware(object):
    def process_request(self, request):
        if request.GET.get('submit'):
            request.method = "POST"
            request.POST = request.GET
