import uuid
from django.db import models


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

    def get_original_url(self, shortened_url):
        objects = super(ShortenedURLComponentManager, self)
        return objects.get(shortened_url=shortened_url).original_url

class ShortenedURLComponent(models.Model):
    original_url = models.TextField()
    shortened_url = models.CharField(max_length=35, db_index=True)
    objects = ShortenedURLComponentManager()

ShortenedURLComponent_IDENTIFIER = 'sh_'


class NavigationSection(models.Model):
    
    name = models.CharField(blank=False, max_length=255)
    order = models.IntegerField(blank=False)
    
    class Meta:
        ordering = ['order']
        abstract = True
    
    def __unicode__(self):
        return self.name

class CategorySection(NavigationSection):
    pass

class TopCouponSection(NavigationSection):
    pass