from django.views.decorators.http import require_POST
import json
import urlparse
from django.http import HttpResponse
from common.url.tldextract import shorten_to_domain
from core.models import Coupon
from core.util import print_stack_trace
from tracking import utils
from tracking.models import ClickTrack


def success():
    return HttpResponse(json.dumps({"status":"1","text":"Success"}))


def _remove_skimlinks(skimlinked_url):
    try:
        parsed = urlparse.urlparse(skimlinked_url)
        query = parsed.query.replace('&amp;','&')
        return urlparse.parse_qs(query)["url"][0]
    except:
        print_stack_trace()
        return skimlinked_url

@require_POST
def click_track(request):
    try:
        referer = utils.u_clean(request.META.get('HTTP_REFERER', 'unknown')[:255])
        clicked_link = request.POST["clicked"][:255]
        try:
            clicked_link=clicked_link.lower()
        except: pass

        source_url_type='landing'
        if '/categories/' in referer:
            source_url_type = 'category'
        elif '/coupons/' in referer:
            source_url_type = 'company'
        elif '/coupon/' in clicked_link:
            source_url_type = 'coupon'

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
            merchant = coupon.merchant
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

        click_track.save()
    except:
        print_stack_trace()
    return success()
