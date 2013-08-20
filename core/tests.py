from django.test import TestCase
from core.models import Coupon


class CouponTest(TestCase):
    # fixtures = ['coupons']
    # Can't get this test to run with the fixtures. Why?

    def test_active_objects(self):
        all_objects = Coupon.objects.count()
        active_objects = Coupon.active_objects.count()
        filtered_objects = Coupon.objects.filter(end_lte=datetime.datetime.now()).count()
        self.assertEqual(active_objects, (all_objects - filtered_objects))
