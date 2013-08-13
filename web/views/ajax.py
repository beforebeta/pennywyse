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


