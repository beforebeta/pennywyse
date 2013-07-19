from django.conf import settings
from websvcs.models import EmailSubscription

def base(request):
    context = {
        'WEBSITE_NAME': settings.WEBSITE_NAME
    }

    #check newsletter subscription
    if "key" in request.session:
        key = request.session["key"]
        if EmailSubscription.objects.filter(session_key=key).count()>0:
            context["SHOW_NEWSLETTER_SUBSCRIPTION_BAR"] = False
        else:
            context["SHOW_NEWSLETTER_SUBSCRIPTION_BAR"] = True

    return context