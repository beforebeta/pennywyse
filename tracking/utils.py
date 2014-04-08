import csv
import datetime
import os
import re
import simplejson as json
import shutil
import unicodedata
import urllib
from urlparse import urlparse, parse_qs

from django.conf import settings
from redis import Redis

# this is not intended to be an all-knowing IP address regex
IP_RE = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

ADWORDS_EXPORT_FILE = 'adwords_report.csv'
FB_ADS_EXPORT_FILE = 'fb_report.csv'

def get_ip(request):
    """
    Retrieves the remote IP address from the request data.  If the user is
    behind a proxy, they may have a comma-separated list of IP addresses, so
    we need to account for that.  In such a case, only the first IP in the
    list will be retrieved.  Also, some hosts that use a proxy will put the
    REMOTE_ADDR into HTTP_X_FORWARDED_FOR.  This will handle pulling back the
    IP from the proper place.
    """

    # if neither header contain a value, just use local loopback
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR',
                                  request.META.get('REMOTE_ADDR', '127.0.0.1'))
    if ip_address:
        # make sure we have one and only one IP
        try:
            ip_address = IP_RE.match(ip_address)
            if ip_address:
                ip_address = ip_address.group(0)
            else:
                # no IP, probably from some dirty proxy or other device
                # throw in some bogus IP
                ip_address = '10.0.0.1'
        except IndexError:
            pass

    return ip_address

def get_timeout():
    """
    Gets any specified timeout from the settings file, or use 10 minutes by
    default
    """
    return getattr(settings, 'TRACKING_TIMEOUT', 10)

def get_cleanup_timeout():
    """
    Gets any specified visitor clean-up timeout from the settings file, or
    use 24 hours by default
    """
    return getattr(settings, 'TRACKING_CLEANUP_TIMEOUT', 24)

def u_clean(s):
    """A strange attempt at cleaning up unicode"""

    uni = ''
    try:
        # try this first
        uni = str(s).decode('iso-8859-1')
    except UnicodeDecodeError:
        try:
            # try utf-8 next
            uni = str(s).decode('utf-8')
        except UnicodeDecodeError:
            # last resort method... one character at a time (ugh)
            if s and type(s) in (str, unicode):
                for c in s:
                    try:
                        uni += unicodedata.normalize('NFKC', unicode(c))
                    except UnicodeDecodeError:
                        uni += '-'

    return uni.encode('ascii', 'xmlcharrefreplace')

def fetch_ad_costs():
    from tracking.models import AdCost
    if not os.path.exists('processed'):
        os.mkdir('processed')
    try:
        with open(ADWORDS_EXPORT_FILE, 'rb') as csvfile:
            print 'Importing Ad Costs data from AdWords'
            rows = csv.reader(csvfile, delimiter=',')
            for row in rows:
                if len(row) == 19:
                    try:
                        datetime.datetime.strptime(row[0], "%m/%d/%y")
                        adcost, created = AdCost.objects.get_or_create(start_date=row[0], campaign=row[3], ad=row[4], keyword=row[2],
                                                 impression=row[10], clicks=row[9], costs=row[13], average_cpc=row[11],
                                                 acquisition_source='PPC', acquisition_medium='PPCad', acquisition_term=row[2],
                                                 acquisition_campaign=row[3])
                        if created:
                            print 'Exported campaign %s' % row[3]
                        else:
                            print 'Skipped campaign %s' % row[3]
                    except:
                        print 'Row skipped, incorrect date format, %s' % row[0]
        destination_path = os.path.join('processed', 'adword_costs_%s.csv' % datetime.datetime.now().strftime('%b-%d-%I%M%p-%G'))
        shutil.move(ADWORDS_EXPORT_FILE, destination_path)
    except IOError:
        print '%s cannot be opened' % ADWORDS_EXPORT_FILE
    
    try:
        with open(FB_ADS_EXPORT_FILE, 'rb') as csvfile:
            print 'Importing Ad Costs data from Facebook Ads'
            rows = csv.reader(csvfile, delimiter=',')
            rows.next()    # skipping first line
            for row in rows:
                if len(row) >= 15:
                    adcost, created = AdCost.objects.get_or_create(start_date=row[0], campaign=row[3], impression=row[3], 
                                                social_impression=row[4], clicks=row[5], costs=row[10], average_cpc=row[8], 
                                                frequency=row[11], actions=row[12], unique_clicks=row[13], acquisition_source='mw', 
                                                acquisition_medium='facebook', acquisition_campaign=row[3])
                    if created:
                        print 'Exported campaign %s' % row[3]
                    else:
                        print 'Skipped campaign %s' % row[3]
        destination_path = os.path.join('processed', 'fb_costs_%s.csv' % datetime.datetime.now().strftime('%b-%d-%I%M%p-%G'))
        shutil.move(FB_ADS_EXPORT_FILE, destination_path)
    except IOError:
        print '%s cannot be opened' % FB_ADS_EXPORT_FILE
        
def aggregate_visitor_data():
    from tracking.models import SearchQueryLog, Visitor
    redis = Redis()
    print 'Processing visitor data'
    for key in redis.keys('visitor_data_*'):
        redis_data = redis.get(key)
        if redis_data:
            visitor_data = json.loads(redis_data)
            visitor_id = visitor_data.get('visitor_id', None)
            if visitor_id:
                try:
                    visitor = Visitor.objects.get(pk=visitor_id)
                except Visitor.DoesNotExist:
                    continue
                visitor.bump_past_acquisition_info()
                for k in ['url', 'referrer', 'user_agent', 
                          'acquisition_source', 'acquisition_medium', 
                          'acquisition_term', 'acquisition_content',
                          'acquisition_campaign']:
                        v = visitor_data.get(k, None)
                        if v:
                            setattr(visitor, k, v)
                past_acquisition_info = visitor_data.get('past_acquisition_info', [])
                if past_acquisition_info:
                    visitor.past_acquisition_info += past_acquisition_info
                if not visitor.session_start:
                    session_start = int(visitor_data['session_start'])
                    visitor.session_start = datetime.datetime.utcfromtimestamp(session_start)
                visitor.page_views += visitor_data.get('page_views', 0)
                last_update = int(visitor_data['last_update'])
                visitor.last_update = datetime.datetime.utcfromtimestamp(last_update)
                visitor.save()
                redis.delete(key)
            print 'Processed visitor %s' % visitor_id
        else:
            print 'Error with key %s' % key

    print 'Processing search query data'
    for key in redis.keys('search_query_data_*'):
        redis_data = redis.get(key)
        if redis_data:
            search_query_data = json.loads(redis_data)
            visitor_id = search_query_data.get('visitor_id', None)
            found_coupons = search_query_data.get('found_coupons', 0)
            found_merchants = search_query_data.get('found_merchants', 0)
            redirected = search_query_data.get('redirected', False)
            query = search_query_data.get('query', None)
            date_added = search_query_data.get('date_added', None)
            try:
                visitor = Visitor.objects.get(pk=visitor_id)
            except Visitor.DoesNotExist:
                visitor = None
            redirection_track = SearchQueryLog.objects.create(query=query, visitor=visitor,
                                                              found_coupons=found_coupons, found_merchants=found_merchants,
                                                              redirected=redirected)
            redirection_track.date_added = datetime.datetime.utcfromtimestamp(date_added)
            redirection_track.save()
            redis.delete(key)
            print 'Processed search query data %s' % visitor_id
        else:
            print 'Error with key %s' % key 
                
    print 'Processing acqusition sources'
    for visitor in Visitor.objects.filter(acquisition_source__in=['unknown','direct']):
        parsed_url = urlparse(visitor.referrer)
        params = parse_qs(parsed_url.query)
        source = search_query = None
        if parsed_url.netloc == 'www.bing.com' or parsed_url.netloc.find('search.yahoo.') != -1\
                                            or re.search('.*google[\.][a-z]{1,4}', parsed_url.netloc):
            source = parsed_url.netloc
        if parsed_url.netloc == 'www.bing.com' and parsed_url.path == '/search':
            search_query = params.get('q', [])
        if parsed_url.netloc.find('search.yahoo.') != -1 and parsed_url.path == '/search':
            search_query = params.get('p', [])
        if re.search('.*google[\.][a-z]{1,4}', parsed_url.netloc) and parsed_url.path == '/search':
            search_query = params.get('q', [])
        if source:
            visitor.bump_past_acquisition_info()
            visitor.acquisition_source = source
            visitor.acquisition_medium = 'organic'
            if search_query:
                print 'Updated visitor info, source: %s, keyword: %s' % (source, search_query[0])
                visitor.acquisition_term = search_query[0]
            else:
                print 'Updated visitor info, source: %s' % source
            visitor.save()

def get_visitor_tag(url, visitor_id):
    from core.util import print_stack_trace
    try:
        if 'go.redirectingat.com' in url:
            parsed = urlparse(url)
            query_dict = parse_qs(parsed.query)
            for key in query_dict.keys():
                query_dict[key] = query_dict[key][0]
            if not 'xcust' in query_dict.keys():
                query_dict['xcust'] = ''
            query_dict['xcust'] = visitor_id
            url = query_dict['url']
            del query_dict['url']
            return 'http://go.redirectingat.com/?%s&%s' % (urllib.urlencode(query_dict),
                                                           urllib.urlencode({'url':url}))
        else:
            return url
    except:
        print_stack_trace()
        return url

def generate_skimlinks_url(url):
    params = {'xs': 1, 'id': settings.SKIMLINKS_SITE_ID}
    return 'http://go.redirectingat.com/?%s&%s' % (urllib.urlencode(params),
                                                   urllib.urlencode({'url':url}))
