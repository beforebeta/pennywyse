from haystack.signals import BaseSignalProcessor
from models import update_object, Coupon

class CouponSignalProcessor(BaseSignalProcessor):
    def setup(self):
        update_object.connect(self.handle_save, sender=Coupon)
