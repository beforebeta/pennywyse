from datetime import datetime, timedelta
import logging
import traceback

from django.contrib.gis.utils import HAS_GEOIP
from core.models import Merchant, Coupon

if HAS_GEOIP:
    from django.contrib.gis.utils import GeoIP, GeoIPException

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from tracking import utils

USE_GEOIP = getattr(settings, 'TRACKING_USE_GEOIP', False)
CACHE_TYPE = getattr(settings, 'GEOIP_CACHE_TYPE', 4)

log = logging.getLogger('tracking.models')
from picklefield.fields import PickledObjectField

class VisitorManager(models.Manager):
    def active(self, timeout=None):
        """
        Retrieves only visitors who have been active within the timeout
        period.
        """
        if not timeout:
            timeout = utils.get_timeout()

        now = datetime.now()
        cutoff = now - timedelta(minutes=timeout)

        return self.get_query_set().filter(last_update__gte=cutoff)

class Visitor(models.Model):
    session_key         = models.CharField(max_length=40)
    ip_address          = models.CharField(max_length=20)
    user                = models.ForeignKey(User, null=True)
    user_agent          = models.CharField(max_length=255)
    referrer            = models.CharField(max_length=255)
    url                 = models.CharField(max_length=255)
    page_views          = models.PositiveIntegerField(default=0)
    session_start       = models.DateTimeField()
    last_update         = models.DateTimeField()

    """
    There are a total of five parameters. We recommend you always use utm_source, utm_medium, and utm_campaign for every link you own to keep track of your referral traffic. utm_term and utm_content can be used for tracking additional information:

    utm_source: Identify the advertiser, site, publication, etc. that is sending traffic to your property, e.g. google, citysearch, newsletter4, billboard.
    utm_medium: The advertising or marketing medium, e.g.: cpc, banner, email newsletter.
    utm_campaign: The individual campaign name, slogan, promo code, etc. for a product.
    utm_term: Identify paid search keywords. If you're manually tagging paid keyword campaigns, you should also use utm_term to specify the keyword.
    utm_content: Used to differentiate similar content, or links within the same ad. For example, if you have two call-to-action links within the same email message, you can use utm_content and set different values for each so you can tell which version is more effective.
    Next: URL builder
    """

    acquisition_source      = models.CharField(max_length=255, default="direct")
    acquisition_medium      = models.CharField(max_length=255, default="direct")
    acquisition_term        = models.CharField(max_length=255, default="direct")
    acquisition_content     = models.CharField(max_length=255, default="direct")
    acquisition_campaign    = models.CharField(max_length=255, default="direct")
    acquisition_gclid       = models.CharField(max_length=255, default="direct")

    past_acquisition_info   = PickledObjectField(default=[])

    date_added          = models.DateTimeField(default=datetime.now(), auto_now_add=True)
    last_modified       = models.DateTimeField(default=datetime.now(), auto_now=True, auto_now_add=True)

    objects = VisitorManager()

    def bump_past_acquisition_info(self):
        #dont bump if this person was earlier direct - because that might lead to many direct bumps
        if self.acquisition_medium == "direct" and \
           self.acquisition_campaign == "direct":
            return
        self.past_acquisition_info.append({
            "date_valid_until"      : datetime.now(),
            "acquisition_source"    : self.acquisition_source,
            "acquisition_medium"    : self.acquisition_medium,
            "acquisition_term"      : self.acquisition_term,
            "acquisition_content"   : self.acquisition_content,
            "acquisition_campaign"  : self.acquisition_campaign,
            "acquisition_gclid"     : self.acquisition_gclid
        })

    def _time_on_site(self):
        """
        Attempts to determine the amount of time a visitor has spent on the
        site based upon their information that's in the database.
        """
        if self.session_start:
            seconds = (self.last_update - self.session_start).seconds

            hours = seconds / 3600
            seconds -= hours * 3600
            minutes = seconds / 60
            seconds -= minutes * 60

            return u'%i:%02i:%02i' % (hours, minutes, seconds)
        else:
            return ugettext(u'unknown')
    time_on_site = property(_time_on_site)

    def _get_geoip_data(self):
        """
        Attempts to retrieve MaxMind GeoIP data based upon the visitor's IP
        """

        if not HAS_GEOIP or not USE_GEOIP:
            # go no further when we don't need to
            log.debug('Bailing out.  HAS_GEOIP: %s; TRACKING_USE_GEOIP: %s' % (HAS_GEOIP, USE_GEOIP))
            return None

        if not hasattr(self, '_geoip_data'):
            self._geoip_data = None
            try:
                gip = GeoIP(cache=CACHE_TYPE)
                self._geoip_data = gip.city(self.ip_address)
            except GeoIPException:
                # don't even bother...
                log.error('Error getting GeoIP data for IP "%s": %s' % (self.ip_address, traceback.format_exc()))

        return self._geoip_data

    geoip_data = property(_get_geoip_data)

    def _get_geoip_data_json(self):
        """
        Cleans out any dirty unicode characters to make the geoip data safe for
        JSON encoding.
        """
        clean = {}
        if not self.geoip_data: return {}

        for key,value in self.geoip_data.items():
            clean[key] = utils.u_clean(value)
        return clean

    geoip_data_json = property(_get_geoip_data_json)

    class Meta:
        ordering = ('-last_update',)
        unique_together = ('session_key', 'ip_address',)

class UntrackedUserAgent(models.Model):
    keyword = models.CharField(_('keyword'), max_length=100, help_text=_('Part or all of a user-agent string.  For example, "Googlebot" here will be found in "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" and that visitor will not be tracked.'))
    date_added          = models.DateTimeField(default=datetime.now(), auto_now_add=True)
    last_modified       = models.DateTimeField(default=datetime.now(), auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.keyword

    class Meta:
        ordering = ('keyword',)
        verbose_name = _('Untracked User-Agent')
        verbose_name_plural = _('Untracked User-Agents')

class BannedIP(models.Model):
    ip_address = models.IPAddressField('IP Address', help_text=_('The IP address that should be banned'))
    date_added          = models.DateTimeField(default=datetime.now(), auto_now_add=True)
    last_modified       = models.DateTimeField(default=datetime.now(), auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.ip_address

    class Meta:
        ordering = ('ip_address',)
        verbose_name = _('Banned IP')
        verbose_name_plural = _('Banned IPs')


class ClickTrack(models.Model):
    """ A new instance is created whenever a merchant link is clicked and potential revenue is earned:
    Two major instances:
    1. Visit Page Click on the Coupon Page
    2. Coupon Specific Page"""
    visitor             = models.ForeignKey(Visitor, null=True, blank=True)
    # we add some of the fields that are already in visitor because we need to know the exact
    # values when the click happened and because these values change in the visitor field
    user_agent          = models.CharField(max_length=255, null=True, blank=True)
    referer            = models.CharField(max_length=255, null=True, blank=True)
    # target url at merchant
    target_url          = models.CharField(max_length=255, null=True, blank=True)
    # coupon url or company page url
    source_url          = models.CharField(max_length=255, null=True, blank=True)
    source_url_type     = models.CharField(max_length=10, null=True, blank=True) #'COUPON', 'COMPANY'
    merchant_domain     = models.CharField(max_length=255, null=True, blank=True)

    merchant            = models.ForeignKey(Merchant, null=True, blank=True)
    coupon              = models.ForeignKey(Coupon, null=True, blank=True)

    date                = models.DateField(default=datetime.today())
    date_added          = models.DateTimeField(default=datetime.now(), auto_now_add=True)
    last_modified       = models.DateTimeField(default=datetime.now(), auto_now=True, auto_now_add=True)

class Commission(models.Model):
    commissionID        = models.CharField(max_length=255, null=True, blank=True, db_index=True, unique=True)
    commissionType      = models.CharField(max_length=255, null=True, blank=True)
    commissionValue     = models.FloatField(default=0) #in dollars
    currency            = models.CharField(max_length=10, null=True, blank=True)
    customID            = models.CharField(max_length=50, null=True, blank=True)
    date                = models.DateField(blank=True, null=True)
    domainID            = models.CharField(max_length=255, null=True, blank=True)
    merchantID          = models.CharField(max_length=255, null=True, blank=True)
    publisherID         = models.CharField(max_length=255, null=True, blank=True)
    items               = models.IntegerField(default=0)
    sales               = models.IntegerField(default=0)
    remoteReferer       = models.TextField(default="")
    remoteUserAgent     = models.TextField(default="")
    url                 = models.CharField(max_length=255, null=True, blank=True)
    domain              = models.CharField(max_length=255, null=True, blank=True)
    status              = models.CharField(max_length=255, null=True, blank=True)


