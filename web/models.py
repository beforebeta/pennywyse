import datetime
import uuid
from django.db import models
from core.models import Merchant, Coupon

class FeaturedCoupon(models.Model):
    coupon = models.ForeignKey(Coupon)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return str(self.coupon)

class NewCoupon(models.Model):
    coupon = models.ForeignKey(Coupon)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return str(self.coupon)

class PopularCoupon(models.Model):
    coupon = models.ForeignKey(Coupon)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return str(self.coupon)

class ShortenedURLComponentManager(models.Manager):
    def shorten_url_component(self, original_url):
        objects = super(ShortenedURLComponentManager, self)
        original_url = original_url.strip()
        try:
            existing_shortened_url = objects.get(original_url=original_url)
            return existing_shortened_url
        except:
            shortened_url = ShortenedURLComponent(original_url=original_url, shortened_url="%s%s" % (ShortenedURLComponent_IDENTIFIER, uuid.uuid4().hex))
            shortened_url.save()
            return shortened_url

    def is_shortened_url(self, url):
        if not url:
            return False
        if len(url) < 3:
            return False
        if url[:3] == ShortenedURLComponent_IDENTIFIER:
            return True

#    def should_shorten_url(self, url):
#        if len(url) > 255:
#            return True
#        else:
#            return False

    def get_original_url(self, shortened_url):
        objects = super(ShortenedURLComponentManager, self)
        return objects.get(shortened_url=shortened_url).original_url

class ShortenedURLComponent(models.Model):
    original_url = models.TextField()
    shortened_url = models.CharField(max_length=35, db_index=True)
    objects = ShortenedURLComponentManager()

ShortenedURLComponent_IDENTIFIER = 'sh_'