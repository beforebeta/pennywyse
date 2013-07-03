from django.conf import settings

def base(request):
    context = {
        'WEBSITE_NAME': settings.WEBSITE_NAME
    }
    return context