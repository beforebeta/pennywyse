from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal

from haystack.signals import BaseSignalProcessor
from models import Coupon, Category, Merchant, MerchantAffiliateData


@receiver(post_save, sender=Category)
@receiver(post_save, sender=Coupon)
@receiver(post_save, sender=Merchant)
@receiver(post_save, sender=MerchantAffiliateData)
def invalidate_cache(sender, instance, **kwargs):
    cache.clear()

# Signal for triggering single coupon update in search index
update_object = Signal(providing_args=["instance", "sender"])

# Signal for triggering single coupon deletion from search index
delete_object = Signal(providing_args=["instance", "sender"])

class CouponSignalProcessor(BaseSignalProcessor):
    """Subclassing haystack generic signal class to connect it to custom signals."""
    
    def setup(self):
        update_object.connect(self.handle_save, sender=Coupon)
        delete_object.connect(self.handle_delete, sender=Coupon)
        models.signals.post_delete.connect(self.handle_delete, sender=Coupon)
    
    def teardown(self):
        update_object.disconnect(self.handle_save, sender=Coupon)
        delete_object.disconnect(self.handle_delete, sender=Coupon)
        models.signals.post_delete.disconnect(self.handle_delete, sender=Coupon)