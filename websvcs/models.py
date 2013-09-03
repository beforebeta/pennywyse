import datetime
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.db import models
import uuid
from picklefield.fields import PickledObjectField

from django.conf import settings
import urllib, gzip, os, base64
from cPickle import dumps, loads
from core.util import print_stack_trace
from vendor.embedly import Embedly

class ImageStore(models.Model):
    remote_url = models.CharField(max_length=255, db_index=True)
    local_url = models.CharField(max_length=255, db_index=True)
    source_user = models.ForeignKey(User, blank=True)

    width = models.IntegerField(default=-1)
    height = models.IntegerField(default=-1)

    date_added = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return "%s -> %s" % (self.remote_url, self.local_url)

    def save(self, *args, **kwargs):
        if self.remote_url:
            if ShortenedURL.objects.should_shorten_url(self.remote_url):
                self.remote_url = ShortenedURL.objects.shorten_url(self.remote_url).shortened_url
        super(ImageStore, self).save(*args, **kwargs)

##################################################################
# Shortened URL
##################################################################

class ShortenedURLManager(models.Manager):
    def shorten_url(self, original_url):
        objects = super(ShortenedURLManager, self)
        original_url = original_url.strip()
        try:
            existing_shortened_url = objects.get(original_url=original_url)
            return existing_shortened_url
        except:
            shortened_url = ShortenedURL(original_url=original_url, shortened_url="%s%s" % (ShortenedURL_IDENTIFIER, uuid.uuid4().hex))
            shortened_url.save()
            return shortened_url

    def is_shortened_url(self, url):
        if not url:
            return False
        if len(url) < 7:
            return False
        if url[:7] == ShortenedURL_IDENTIFIER:
            return True

    def should_shorten_url(self, url):
        if len(url) > 255:
            return True
        else:
            return False

    def get_original_url(self, shortened_url):
        objects = super(ShortenedURLManager, self)
        return objects.get(shortened_url=shortened_url).original_url

class ShortenedURL(models.Model):
    original_url = models.TextField()
    shortened_url = models.CharField(max_length=40, db_index=True)
    objects = ShortenedURLManager()

ShortenedURL_IDENTIFIER = '#SHORT-'

##################################################################
# Email Subscriptions
##################################################################

class EmailSubscription(models.Model):
    app         = models.CharField(max_length=255, db_index=True)
    session_key = models.CharField(max_length=255, db_index=True)
    email       = models.CharField(max_length=255, db_index=True)
    first_name  = models.CharField(max_length=255, null=True, blank=True)
    last_name   = models.CharField(max_length=255, null=True, blank=True)
    full_name   = models.CharField(max_length=255, null=True, blank=True)
    context     = PickledObjectField(default={})

    date_added = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return "%s, %s, %s" % (self.app, self.email, self.full_name)

    def __unicode__(self):  # Python 3: def __str__(self):
        return "%s %s" % (self.app, self.email)

class EmbedlyCache:
    def __init__(self):
        self.cache_loc = settings.DOWNLOADER_CACHE_LOCATION
        self.cache = {}
        self.client = Embedly(settings.EMBEDLY_KEY)
        print "Loading in Embedly Cache-Start. Wait for End confirmation..."
        try:
            os.makedirs(self.cache_loc)
        except:
            pass
        for file in os.listdir(self.cache_loc):
            file = os.path.join(self.cache_loc, file)
            if os.path.isfile(file):
                filename = os.path.basename(file)
                self.cache[self.path2url(filename)] = file
        print "End. Finished loading Embedly Cache."

    def get(self, url, stateless_params=""):
        try:
            f = gzip.open(self.cache[url], 'rb')
            file_contents = loads(f.read())
            print '!!!!!!!!!!!!!!!!!!!!!!!loads!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print file_contents.data
            if "error_code" in file_contents.data:
                print "*"*100
                print "Deleting cache for", url
                print "*"*100
                self.delete_cache(url)
                f.close()
                raise KeyError #go into the except block
            f.close()
            return file_contents
        except KeyError:
            filename = os.path.join(self.cache_loc, self.url2path(url))
            url_contents = self.client.extract(url)

            if ('title' in url_contents) and (url_contents['title'] == 'error'):
              raise Exception('Embedly Exception', url)

            if len(filename) < 255:
              f = gzip.open(filename, 'wb')
              print '!!!!!!!!!!!!!!!!!!!!!!!dumps!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
              f.write(dumps(url_contents))
              f.close()
            print url_contents.data

            self.cache[url] = filename
            return url_contents

    def delete_cache(self, url):
        try:
            filename = os.path.join(self.cache_loc, self.url2path(url))
            os.remove(filename)
            del self.cache[url]
        except:
            pass

    def url2path(self, url):
        print url
        return base64.urlsafe_b64encode(url)

    def path2url(self, path):
        return base64.urlsafe_b64decode(path)

cache = EmbedlyCache()

class EmbedlyMerchant:
  def __init__(self, merchant):
    self.merchant = merchant
    active = self.merchant.coupon_set.filter(Q(end__gt=datetime.datetime.now()) | Q(end__isnull=True))
    self.coupons = [EmbedlyCoupon(coupon) for coupon in active]

  def update_coupons(self):
        for coupon in self.coupons:
            try:
                coupon.update()
            except:
                print_stack_trace()


class EmbedlyCoupon:
  def __init__(self, coupon):
    self.coupon = coupon

  def link(self):
    link = self.coupon.directlink
    if not link:
      link = self.coupon.link
    if link[-1] == "+":
      link = link[0:-1]
    return link

  def update(self):
    try:
      if self.link():
        print self.link()
        extract = cache.get(self.link())
        if ('description' in extract) and extract['description'] != self.coupon.merchant.description:
          if 'title' in extract:
            self.coupon.embedly_title = extract['title']
          if ('description' in extract):
            self.coupon.embedly_description = extract['description']
          if ('images' in extract) and extract['images'] and 'url' in extract['images'][0]:
            self.coupon.embedly_image_url = extract['images'][0]['url']
            print "For:    {0}\nEmbedly returned:   {1}".format(self.link(), self.coupon.embedly_image_url)
          self.coupon.save()
          print "extracted data for Coupon #{0}:    {1}\n  Merchant:      {2}\n\n\n".format(self.coupon.id, self.coupon.local_path(), self.coupon.merchant.local_path())
        else:
          print "\n\n\nno extract for Coupon #{0}   Merchant#{1}\n\n\nCoupon Description Matches Merchant Description\n\n\n\n".format(self.coupon.id, self.coupon.merchant.id)
    except:
      print "failed to extract data for Coupon #{0}".format(self.coupon.id)
