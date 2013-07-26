from django.conf import settings
from websvcs.models import EmailSubscription

def base(request):
    context = {
        'WEBSITE_NAME'  : settings.WEBSITE_NAME,
        "BASE_URL_NO_APPENDED_SLASH" : settings.BASE_URL_NO_APPENDED_SLASH,
        "CURRENT_URL"   : "%s%s" % (settings.BASE_URL_NO_APPENDED_SLASH, request.get_full_path())
    }
    #check newsletter subscription
    if "key" in request.session:
        key = request.session["key"]
        if EmailSubscription.objects.filter(session_key=key).count()>0:
            context["SHOW_NEWSLETTER_SUBSCRIPTION_BAR"] = False
        else:
            context["SHOW_NEWSLETTER_SUBSCRIPTION_BAR"] = True
    else:
        context["SHOW_NEWSLETTER_SUBSCRIPTION_BAR"] = True

    return context