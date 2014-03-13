from datetime import datetime, timedelta
import logging
import re
import traceback
import simplejson as json

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.utils import DatabaseError
from core.util import print_stack_trace

from tracking import utils
from tracking.models import Visitor, UntrackedUserAgent
import pytz
from redis import Redis
import time

log = logging.getLogger('tracking.middleware')

VISITOR_PARAMS_MAPPING = {'acquisition_source': 'utm_source',
                          'acquisition_medium': 'utm_medium',
                          'acquisition_term': 'utm_term',
                          'acquisition_content': 'utm_content',
                          'acquisition_campaign': 'utm_campaign'}

GA_PARAMS_MAP = {'(direct)': 'direct',
                '(none)': None,
                '(notset)': None}

redis = Redis()

class VisitorTrackingMiddleware(object):
    """
    Keeps track of your active users.  Anytime a visitor accesses a valid URL,
    their unique record will be updated with the page they're on and the last
    time they requested a page.

    Records are considered to be unique when the session key and IP address
    are unique together.  Sometimes the same user used to have two different
    records, so I added a check to see if the session key had changed for the
    same IP and user agent in the last 5 minutes
    """

    @property
    def prefixes(self):
        """Returns a list of URL prefixes that we should not track"""

        if not hasattr(self, '_prefixes'):
            self._prefixes = getattr(settings, 'NO_TRACKING_PREFIXES', [])

            if not getattr(settings, '_FREEZE_TRACKING_PREFIXES', False):
                for name in ('MEDIA_URL', 'STATIC_URL'):
                    url = getattr(settings, name)
                    if url and url != '/':
                        self._prefixes.append(url)

                try:
                    # finally, don't track requests to the tracker update pages
                    self._prefixes.append(reverse('tracking-refresh-active-users'))
                except NoReverseMatch:
                    # django-tracking hasn't been included in the URLconf if we
                    # get here, which is not a bad thing
                    pass

                settings.NO_TRACKING_PREFIXES = self._prefixes
                settings._FREEZE_TRACKING_PREFIXES = True

        return self._prefixes

    def process_request(self, request):
        # don't process AJAX requests
        if request.path.startswith("/s/") or request.path.startswith("/static/") or request.path.startswith("/admin/")\
             or request.path.startswith("/favicon.ico") or (request.is_ajax() and not request.path.startswith('/o/')):
            return
        # create some useful variables
        ip_address = utils.get_ip(request)
        user_agent = unicode(request.META.get('HTTP_USER_AGENT', '')[:255], errors='ignore')

        # retrieve untracked user agents from cache
        ua_key = '_tracking_untracked_uas'
        untracked = cache.get(ua_key)
        if untracked is None:
            log.info('Updating untracked user agent cache')
            untracked = UntrackedUserAgent.objects.all()
            cache.set(ua_key, untracked, 3600)

        # see if the user agent is not supposed to be tracked
        for ua in untracked:
            # if the keyword is found in the user agent, stop tracking
            if user_agent.find(ua.keyword) != -1:
                log.debug('Not tracking UA "%s" because of keyword: %s' % (user_agent, ua.keyword))
                return

        if hasattr(request, 'session') and request.session.session_key:
            # use the current session key if we can
            session_key = request.session.session_key
        else:
            # otherwise just fake a session key
            session_key = '%s:%s' % (ip_address, user_agent)
            session_key = session_key[:40]

        # ensure that the request.path does not begin with any of the prefixes
        for prefix in self.prefixes:
            if request.path.startswith(prefix):
                log.debug('Not tracking request to: %s' % request.path)
                return

        # if we get here, the URL needs to be tracked
        # determine what time it is
        now = datetime.now()

        attrs = {
            'session_key': session_key,
            'ip_address': ip_address
        }
        
        visitor_id = request.session.get('visitor_id', None)
        if not visitor_id:
            # for some reason, Visitor.objects.get_or_create was not working here
            try:
                visitor = Visitor.objects.only('id').get(**attrs)
            except Visitor.DoesNotExist:
                request.session.set_test_cookie()
                # see if there's a visitor with the same IP and user agent
                # within the last 5 minutes
                cutoff = now - timedelta(minutes=5)
                visitors = Visitor.objects.only('id').filter(
                    ip_address=ip_address,
                    user_agent=user_agent,
                    last_update__gte=cutoff
                )
    
                if len(visitors):
                    visitor = visitors[0]
                    visitor.session_key = session_key
                    log.debug('Using existing visitor for IP %s / UA %s: %s' % (ip_address, user_agent, visitor.id))
                else:
                    # it's probably safe to assume that the visitor is brand new
                    visitor = Visitor(**attrs)
                    log.debug('Created a new visitor: %s' % attrs)
                try:
                    visitor.save()
                except DatabaseError:
                    print_stack_trace()
                    log.error('There was a problem saving visitor information:\n%s\n\n%s' % (traceback.format_exc(), locals()))
            except:
                return
            
            request.session['visitor_id'] = visitor_id = visitor.id

        redis_data = redis.get('visitor_data_%s' % visitor_id) or '{}'
        visitor_data = json.loads(redis_data)
        visitor_data['visitor_id'] = visitor_id

        # update the tracking information
        visitor_data['user_agent'] = user_agent

        # if the visitor record is new, or the visitor hasn't been here for
        # at least an hour, update their referrer URL
        one_hour_ago = pytz.UTC.localize(now - timedelta(hours=1))
        # TODO: ensure that we are on the same time zone - I just put UTC for now
        # to get it working
        last_update = visitor_data.get('last_update', None)
        if not last_update or last_update <= time.mktime(one_hour_ago.timetuple()):
            visitor_data['referrer'] = utils.u_clean(request.META.get('HTTP_REFERER', 'unknown')[:255])

            # reset the number of pages they've been to
            visitor_data['page_views'] = 0
            visitor_data['session_start'] = time.mktime(now.timetuple())

        visitor_data['url'] = request.path
        page_views = visitor_data.get('page_views', 0) + 1
        visitor_data['page_views'] = page_views
        visitor_data['last_update'] = time.mktime(now.timetuple())

        try:
            # Extracting visitor data from GA cookie
            cookie = request.COOKIES.get('__utmz')
            if cookie:
                try:
                    data = cookie.split('.', 4)[-1]
                    data = dict(match.groups() for match in re.finditer(
                        r'(utm(?:csr|ccn|cmd|ctr))=([^\|]*)', data))
                except (ValueError, IndexError):
                    log.error('Malformed GA cookie: {0!r}'.format(cookie))
                else:
                    visitor_data['source'] = normalize_ga_value(data.get('utmcsr'))
                    visitor_data['medium'] = normalize_ga_value(data.get('utmcmd'))
                    visitor_data['campaign'] = normalize_ga_value(data.get('utmccn'))
                    visitor_data['keywords'] = normalize_ga_value(data.get('utm.ctr'))
            
            utm_source = request.GET.get("utm_source", "unknown")
            request.session['acquisition_source_name'] = utm_source

            if utm_source != "unknown":
                # utm_source: Identify the advertiser, site, publication, etc. that is sending traffic to your property, e.g. google, citysearch, newsletter4, billboard.
                # utm_medium: The advertising or marketing medium, e.g.: cpc, banner, email newsletter.
                # utm_campaign: The individual campaign name, slogan, promo code, etc. for a product.
                # utm_term: Identify paid search keywords. If you're manually tagging paid keyword campaigns, you should also use utm_term to specify the keyword.
                # utm_content: Used to differentiate similar content, or links within the same ad. For example, if you have two call-to-action links within the same email message, you can use utm_content and set different values for each so you can tell which version is more effective.

                #update the tracking info with the latest and bump the old one to be stored in the history
                
                #visitor.bump_past_acquisition_info()
                past_acquisition_info = visitor_data.get('past_acquisition_info', [])
                if visitor_data.get('acquisition_source', None):
                    old_visitor_data = {'date_valid_until': time.time()}
                    for k in VISITOR_PARAMS_MAPPING.keys():
                        old_visitor_data[k] = visitor_data.get(k, None)
                    past_acquisition_info.append(old_visitor_data)
                    visitor_data['past_acquisition_info'] = past_acquisition_info
                for k,v in VISITOR_PARAMS_MAPPING.items():
                    value = request.GET.get(v, 'unknown')[:255]
                    visitor_data[k] = value

        except:
            print_stack_trace()
        redis.set('visitor_data_%s' % visitor_id, json.dumps(visitor_data))
        

def normalize_ga_value(value):
    return GA_PARAMS_MAP.get(value, value)