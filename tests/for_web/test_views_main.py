# import ipdb
# from django.core.urlresolvers import reverse

from django_webtest import WebTest

from web.models import FeaturedCoupon
from core.models import Coupon, Merchant

class MyTestCase(WebTest):

    def test_sample(self):
        dummy_merchant = Merchant.objects.create(name="Dummy Merchant", name_slug='dummy_merchant')
        dummy_coupon = Coupon.objects.create(merchant=dummy_merchant)
        FeaturedCoupon.objects.create(coupon=dummy_coupon)
        home = self.app.get('/')
        # ipdb.set_trace()
        assert home.status_int == 200
