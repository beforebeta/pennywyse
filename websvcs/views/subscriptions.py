from functools import wraps
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils.decorators import available_attrs
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from core.util import print_stack_trace
from websvcs.models import EmailSubscription

def auth_check(func):
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
        if "SECRET_KEY" not in request.POST:
            return HttpResponseBadRequest()
        if request.POST["SECRET_KEY"] != settings.SVCS_SECRET_KEY:
            return HttpResponseBadRequest()
        return func(request, *args, **kwargs)
    return inner

@csrf_exempt
@require_POST
@auth_check
def email_subscribe(request):
    try:
        e = EmailSubscription()
        e.app = request.POST["app"]
        e.email = request.POST["email"]
        e.session_key = request.POST["session_key"]
        try: e.first_name  = request.POST["first_name"]
        except: pass
        try: e.last_name  = request.POST["last_name"]
        except: pass
        try: e.full_name  = request.POST["full_name"]
        except: pass
        try: e.context = request.POST["context"]
        except: pass
        e.save()
        return HttpResponse('1')
    except:
        print_stack_trace()