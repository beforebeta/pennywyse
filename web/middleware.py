from django.conf import settings

class WebMiddleware(object):
    def process_request(self, request):
        request.session.set_expiry(10 * 365 * 24 * 60 * 60) #ten years