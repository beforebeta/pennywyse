import json
import uuid
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import requests
from django.core.validators import validate_email as validate_email_validator
from django.core.exceptions import ValidationError
from common.url.tldextract import shorten_to_domain
from core.models import Coupon
from core.util import print_stack_trace
from tracking import utils
from tracking.models import ClickTrack


def post_message(url, data):
    data["SECRET_KEY"] = settings.SVCS_SECRET_KEY
    r = requests.post("%s%s" % (settings.SVCS_HOST, url), data=data)
    return r.status_code

def validate_email(email):
    try:
        validate_email_validator(email)
        return True
    except ValidationError:
        return False

def success():
    return HttpResponse(json.dumps({"status":"1","text":"Success"}))

@require_POST
def ajax_subscribe(request):
    if not validate_email(request.POST["email"]):
        return HttpResponse(json.dumps({"status":"0","text":"Enter a valid email address"}))
    else:
        if not "key" in request.session:
            request.session["key"] = uuid.uuid4().hex
        post_data=dict()
        post_data["session_key"] = request.session["key"]
        post_data["full_name"] = request.POST["full_name"]
        post_data["email"] = request.POST["email"]
        post_data["app"] = settings.APP_NAME
        post_message("/e/subscribe/", post_data)
        return success()


@require_POST
def click_track(request):
    try:
        source_url_type = ""
        source_url = ""
        clicked_link = request.POST["clicked"][:255]
        referer = utils.u_clean(request.META.get('HTTP_REFERER', 'unknown')[:255])
        coupon=None
        merchant=None

        if "/coupon/" in clicked_link:
            source_url_type = "coupon"
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
            source_url_type = "company"
            target_url = clicked_link
            merchant = None

        merchant_domain = shorten_to_domain(target_url)

        click_track                 = ClickTrack()
        click_track.visitor         = request.visitor
        click_track.user_agent      = request.visitor.user_agent[:255]
        click_track.referrer        = referer[:255]
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