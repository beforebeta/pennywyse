from django.conf import settings
import csv
import re
import unicodedata

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
    try:
        with open(ADWORDS_EXPORT_FILE, 'rb') as csvfile:
            print 'Importing Ad Costs data from AdWords'
            rows = csv.reader(csvfile, delimiter=',')
            for row in rows:
                if len(row) == 18:
                    adcost, created = AdCost.objects.get_or_create(start_date=row[0], campaign=row[3], ad=row[4], keyword=row[2],
                                                 impression=row[10], clicks=row[9], costs=row[13], average_cpc=row[11],
                                                 acquisition_source='PPC', acquisition_medium='PPCad', acquisition_term=row[2],
                                                 acquisition_campaign=row[3])
                    if created:
                        print 'Exported campaign %s' % row[3]
                    else:
                        print 'Skipped campaign %s' % row[3]
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
    except IOError:
        print '%s cannot be opened' % FB_ADS_EXPORT_FILE