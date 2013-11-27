# ipdb.set_trace()
# import ipdb
import unittest
import random

from core.models import DealType, Category, Coupon, Merchant, Country, CouponNetwork, MerchantLocation

class TestCoreModels(unittest.TestCase):

    def test_can_create_coupon(self):
        c = Coupon.objects.create()
        self.assertTrue(isinstance(c, Coupon))

    def test_can_create_category(self):
        c = Category.objects.create()
        self.assertTrue(isinstance(c, Category))

    def test_can_create_dealtype(self):
        d = DealType.objects.create()
        self.assertTrue(isinstance(d, DealType))

    def test_can_create_merchant(self):
        m = Merchant.objects.create(name='Dummy Merchant')
        self.assertTrue(isinstance(m, Merchant))

    def test_can_create_country(self):
        c = Country.objects.create()
        self.assertTrue(isinstance(c, Country))

    def test_can_create_couponnetwork(self):
        c = CouponNetwork.objects.create()
        self.assertTrue(isinstance(c, CouponNetwork))

    def test_can_create_merchantlocation(self):
        longitude = random.uniform(-180.0, 180.0)
        latitude = random.uniform(-90.0, 90.0)
        point_wkt = 'POINT({} {})'.format(longitude, latitude)
        m = MerchantLocation.objects.create(geometry=point_wkt)
        self.assertTrue(isinstance(m, MerchantLocation))