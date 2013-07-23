import datetime
from django.contrib.auth.models import User
from django.db import models
import uuid
from picklefield.fields import PickledObjectField

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
        return "%s %s" % (self.app, self.email)
