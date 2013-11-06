from django.conf import settings

from websvcs.models import EmailSubscription


def base(request):
    context = {
        'WEBSITE_NAME'  : settings.WEBSITE_NAME,
        "BASE_URL_NO_APPENDED_SLASH" : settings.BASE_URL_NO_APPENDED_SLASH,
        "CURRENT_URL"   : "%s%s" % (settings.BASE_URL_NO_APPENDED_SLASH, request.get_full_path()),
        "ACQUISITION_SOURCE_LOGO_URL": request.session.get('acquisition_source_logo_url', ''),
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

    if 'custom_landing_url' in request.session:
        context['EXTRA_TAB_URL'] = request.session['custom_landing_url']
        context['EXTRA_TAB_ACTIVE'] = (
            request.path.startswith(request.session['custom_landing_url']))

    return context
