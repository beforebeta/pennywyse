from datetime import timedelta, datetime
from tracking import utils
from tracking.middleware import log
from tracking.models import Visitor
import logging

class VisitorCleanUpMiddleware:
    """Clean up old visitor tracking records in the database"""

    def process_request(self, request):
        timeout = utils.get_cleanup_timeout()

        if str(timeout).isdigit():
            log.debug('Cleaning up visitors older than %s hours' % timeout)
            timeout = datetime.now() - timedelta(hours=int(timeout))
            Visitor.objects.filter(last_update__lte=timeout).delete()
