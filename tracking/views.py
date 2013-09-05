from django.views.decorators.http import require_POST
from functools import wraps
import json
import urlparse
import re
from django.http import HttpResponse
from common.url.tldextract import shorten_to_domain
from core.models import Coupon, Merchant
from core.util import print_stack_trace
from tracking import utils
from tracking.models import ClickTrack


def success():
    return HttpResponse(json.dumps({"status":"1","text":"Success"}))

def _ignore_bots(f):
    @wraps(f)
    def wrapper(request, *args, **kwds):
        try:
            user_agent = unicode(request.META.get('HTTP_USER_AGENT', '')[:255], errors='ignore')
            user_agent = user_agent.lower()
            if "googlebot" in user_agent:
                return success()
            else:
                return f(request, *args, **kwds)
        except:
            return f(request, *args, **kwds)
    return wrapper

def _remove_skimlinks(skimlinked_url):
    try:
        parsed = urlparse.urlparse(skimlinked_url)
        query = parsed.query.replace('&amp;','&')
        return urlparse.parse_qs(query)["url"][0]
    except:
        print_stack_trace()
        return skimlinked_url

@_ignore_bots
def log_click_track(request):
    try:
        referer = utils.u_clean(request.META.get('HTTP_REFERER', 'unknown')[:255])
        clicked_link = request.path
        source_url_type='landing'

        if re.search('/coupons/[a-z0-9-]+/[a-z0-9-]+/[\d]+/', referer):
            source_url_type = 'coupon'
        elif re.search('/coupons/[a-z0-9-]+/', referer):
            source_url_type = 'company'
        elif re.search('/categories/[A-z0-9-]+/', referer):
            source_url_type = 'category'

        coupon=None
        merchant=None

        if "/coupon/" in clicked_link:
            #skimlinks will assume the source url to be the /coupon/ url
            if clicked_link.endswith("/"):
                coupon_id = clicked_link.split("/")[-2] #assumes trailing '/'
            else:
                coupon_id = clicked_link.split("/")[-1]
            source_url = clicked_link
            coupon = Coupon.objects.get(id=int(coupon_id))
            try:
                merchant = Merchant.objects.get(id=coupon.merchant.id)
            except:
                merchant = None
            target_url = coupon.get_retailer_link()
        else:
            source_url = referer
            target_url = clicked_link
            merchant = None

        if 'go.redirectingat.com' in target_url:
            target_url = _remove_skimlinks(target_url)

        merchant_domain = shorten_to_domain(target_url)

        click_track                 = ClickTrack()
        click_track.visitor         = request.visitor
        click_track.user_agent      = request.visitor.user_agent[:255]
        click_track.referer         = referer[:255]
        click_track.target_url      = target_url[:255]
        click_track.source_url_type = source_url_type[:255]
        click_track.source_url      = source_url[:255]
        click_track.merchant        = merchant
        click_track.coupon          = coupon
        click_track.merchant_domain = merchant_domain[:255]

        try:
            click_track.acquisition_source      = request.visitor.acquisition_source
            click_track.acquisition_medium      = request.visitor.acquisition_medium
            click_track.acquisition_term        = request.visitor.acquisition_term
            click_track.acquisition_content     = request.visitor.acquisition_content
            click_track.acquisition_campaign    = request.visitor.acquisition_campaign
            click_track.acquisition_gclid       = request.visitor.acquisition_gclid
        except:
            print_stack_trace()

        try:
            click_track.save()
        except:
            try:
                print "Visitor ID", click_track.visitor
                print "User Agent", click_track.user_agent
                print "Referer", click_track.referer
                print "target_url", click_track.target_url
                print "source_url_type", click_track.source_url_type
                print "merchant", click_track.merchant
                print "coupon", click_track.coupon
                print "merchant_domain", click_track.merchant_domain
                print merchant.name, merchant.id
            except:
                pass
            print_stack_trace()
    except:
        print_stack_trace()

@_ignore_bots
@require_POST
def click_track(request, clicked_link_path=None):
    try:
        referer = utils.u_clean(request.META.get('HTTP_REFERER', 'unknown')[:255])
        clicked_link = request.POST["clicked"][:255]
        try:
            clicked_link=clicked_link.lower()
        except:
            print_stack_trace()

        source_url_type='landing'
        if re.search('/coupons/[a-z0-9-]+/[a-z0-9-]+/[\d]+/', referer):
            source_url_type = 'coupon'
        elif re.search('/coupons/[a-z0-9-]+/', referer):
            source_url_type = 'company'
        elif re.search('/categories/[A-z0-9-]+/', referer):
            source_url_type = 'category'

        coupon=None
        merchant=None

        if "/coupon/" in clicked_link:
            #skimlinks will assume the source url to be the /coupon/ url
            if clicked_link.endswith("/"):
                coupon_id = clicked_link.split("/")[-2] #assumes trailing '/'
            else:
                coupon_id = clicked_link.split("/")[-1]
            source_url = clicked_link
            coupon = Coupon.active_objects.get(id=int(coupon_id))
            try:
                merchant = Merchant.objects.get(id=coupon.merchant.id)
            except:
                merchant = None
            target_url = coupon.get_retailer_link()
        else:
            source_url = referer
            target_url = clicked_link
            merchant = None

        if 'go.redirectingat.com' in target_url:
            target_url = _remove_skimlinks(target_url)

        merchant_domain = shorten_to_domain(target_url)

        click_track                 = ClickTrack()
        click_track.visitor         = request.visitor
        click_track.user_agent      = request.visitor.user_agent[:255]
        click_track.referer         = referer[:255]
        click_track.target_url      = target_url[:255]
        click_track.source_url_type = source_url_type[:255]
        click_track.source_url      = source_url[:255]
        click_track.merchant        = merchant
        click_track.coupon          = coupon
        click_track.merchant_domain = merchant_domain[:255]

        try:
            click_track.acquisition_source      = request.visitor.acquisition_source
            click_track.acquisition_medium      = request.visitor.acquisition_medium
            click_track.acquisition_term        = request.visitor.acquisition_term
            click_track.acquisition_content     = request.visitor.acquisition_content
            click_track.acquisition_campaign    = request.visitor.acquisition_campaign
            click_track.acquisition_gclid       = request.visitor.acquisition_gclid
        except:
            print_stack_trace()

        try:
            click_track.save()
        except:
            try:
                print "Visitor ID", click_track.visitor
                print "User Agent", click_track.user_agent
                print "Referer", click_track.referer
                print "target_url", click_track.target_url
                print "source_url_type", click_track.source_url_type
                print "merchant", click_track.merchant
                print "coupon", click_track.coupon
                print "merchant_domain", click_track.merchant_domain
                print merchant.name, merchant.id
            except:
                pass
            print_stack_trace()
    except:
        print_stack_trace()
    return success()
