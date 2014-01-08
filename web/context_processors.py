from django.conf import settings

from core.models import Category
from web.models import CategorySection, TopCouponSection
from web.forms import EmailSubscriptionForm

def base(request):
    context = {"visitor": getattr(request, 'visitor', None),
               "top_categories": CategorySection.objects.all(),
               "top_coupons": TopCouponSection.objects.all(),
               "top_groceries": Category.objects.filter(name='Grocery Coupons')[0],
               "form": EmailSubscriptionForm(),
               "canonical_url": settings.BASE_URL_NO_APPENDED_SLASH + request.path}
    return context
