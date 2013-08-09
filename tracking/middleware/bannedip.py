from django.http import Http404
from tracking import utils
from django.core.cache import cache
from tracking.middleware import log
from tracking.models import BannedIP


class BannedIPMiddleware:
    """
    Raises an Http404 error for any page request from a banned IP.  IP addresses
    may be added to the list of banned IPs via the Django admin.

    The banned users do not actually receive the 404 error--instead they get
    an "Internal Server Error", effectively eliminating any access to the site.
    """

    def process_request(self, request):
        key = '_tracking_banned_ips'
        ips = cache.get(key)
        if ips is None:
            # compile a list of all banned IP addresses
            log.info('Updating banned IPs cache')
            ips = [b.ip_address for b in BannedIP.objects.all()]
            cache.set(key, ips, 3600)

        # check to see if the current user's IP address is in that list
        if utils.get_ip(request) in ips:
            raise Http404
