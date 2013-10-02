from datetime import datetime, timedelta
import json
import logging
import traceback

from django.contrib.gis.utils import HAS_GEOIP
from common import url
from common.url.tldextract import shorten_to_domain
from core.models import Merchant, Coupon
from core.util import print_stack_trace

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


class AcquisitionSource(models.Model):
    tag = models.CharField(max_length=255, unique=True)
    logo_url = models.CharField(max_length=255)

    def __unicode__(self):
        return self.tag

    class Meta:
        ordering = ('tag',)
        verbose_name = _('Acquisition source')
        verbose_name_plural = _('Acquisition sources')


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
    user                = models.ForeignKey(User, null=True, blank=True)
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

    def save(self, *args, **kwargs):
        super(Visitor, self).save(*args, **kwargs)
        try:
            if self.rev_visitor.all().exists():
                for rv in self.rev_visitor.all():
                    rv.save()
        except:
            print_stack_trace()

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
    source_url_type     = models.CharField(max_length=10, null=True, blank=True) #'COUPON', 'COMPANY', 'LANDING'
    merchant_domain     = models.CharField(max_length=255, null=True, blank=True)

    merchant            = models.ForeignKey(Merchant, null=True, blank=True)
    coupon              = models.ForeignKey(Coupon, null=True, blank=True)

    acquisition_source      = models.CharField(max_length=255, default="direct")
    acquisition_medium      = models.CharField(max_length=255, default="direct")
    acquisition_term        = models.CharField(max_length=255, default="direct")
    acquisition_content     = models.CharField(max_length=255, default="direct")
    acquisition_campaign    = models.CharField(max_length=255, default="direct")
    acquisition_gclid       = models.CharField(max_length=255, default="direct")

    date                = models.DateField(default=datetime.today())
    date_added          = models.DateTimeField(default=datetime.now(), auto_now_add=True)
    last_modified       = models.DateTimeField(default=datetime.now(), auto_now=True, auto_now_add=True)

class RevenueVisitor(models.Model):
    """if we've potentially earned revenue from a visitor we record them here"""
    visitor             = models.ForeignKey(Visitor, blank=True, null=True, related_name='rev_visitor')

    session_key         = models.CharField(max_length=40)
    ip_address          = models.CharField(max_length=20)
    user                = models.ForeignKey(User, null=True, blank=True)
    user_agent          = models.CharField(max_length=255)
    referrer            = models.CharField(max_length=255)
    url                 = models.CharField(max_length=255)
    page_views          = models.PositiveIntegerField(default=0)
    session_start       = models.DateTimeField()
    last_update         = models.DateTimeField()
    acquisition_source      = models.CharField(max_length=255, default="direct")
    acquisition_medium      = models.CharField(max_length=255, default="direct")
    acquisition_term        = models.CharField(max_length=255, default="direct")
    acquisition_content     = models.CharField(max_length=255, default="direct")
    acquisition_campaign    = models.CharField(max_length=255, default="direct")
    acquisition_gclid       = models.CharField(max_length=255, default="direct")

    past_acquisition_info   = PickledObjectField(default=[])

    date_added          = models.DateTimeField(default=datetime.now(), auto_now_add=True)
    last_modified       = models.DateTimeField(default=datetime.now(), auto_now=True, auto_now_add=True)

    date_obj_added      = models.DateTimeField(default=datetime.now(), auto_now_add=True)
    last_obj_modified   = models.DateTimeField(default=datetime.now(), auto_now=True, auto_now_add=True)

    def save(self, *args, **kwargs):
        assert self.visitor, "Visitor object must be provided when creating RevenueVisitor object!"
        if not self.id:
            #only 1 RevenueVisitor object per Visitor object!
            assert not RevenueVisitor.objects.filter(visitor_id=self.visitor.id).exists(), "Only 1 RevenueVisitor per Visitor object!"
            self.id = self.visitor.id
        transfer = lambda r,v,att: setattr(r, att, getattr(v, att))
        transfer(self, self.visitor, 'session_key')
        transfer(self, self.visitor, 'ip_address')
        transfer(self, self.visitor, 'user')
        transfer(self, self.visitor, 'user_agent')
        transfer(self, self.visitor, 'referrer')
        transfer(self, self.visitor, 'url')
        transfer(self, self.visitor, 'page_views')
        transfer(self, self.visitor, 'session_start')
        transfer(self, self.visitor, 'last_update')
        transfer(self, self.visitor, 'page_views')
        transfer(self, self.visitor, 'acquisition_source')
        transfer(self, self.visitor, 'acquisition_medium')
        transfer(self, self.visitor, 'acquisition_term')
        transfer(self, self.visitor, 'acquisition_content')
        transfer(self, self.visitor, 'acquisition_campaign')
        transfer(self, self.visitor, 'acquisition_gclid')
        transfer(self, self.visitor, 'date_added')
        transfer(self, self.visitor, 'last_modified')
        super(RevenueVisitor, self).save(*args, **kwargs)

class CommissionManager(models.Manager):

    def create_from_skimlinks_commissions(self, commissions):
        default_to_empty_string = lambda x: "" if x == None else x
        for c in commissions["skimlinksAccount"]["commissions"].keys():
            try:
                commission = commissions["skimlinksAccount"]["commissions"][c]
                if self.filter(commissionID = commission["commissionID"]).count() > 0:
                    continue #commission already recorded
                comm = Commission(
                    commissionID        = commission["commissionID"],
                    commissionType      = "skimlinks",
                    commissionValue     = float(commission["commissionValue"])/100, #values comes in cents - we convert to dollars)
                    orderValue          = float(commission["orderValue"])/100, #values comes in cents - we convert to dollars)
                    currency            = default_to_empty_string(commission["currency"]),
                    customID            = default_to_empty_string(commission["customID"]),
                    date                = datetime.strptime(commission["date"],"%Y-%m-%d").date(),
                    domainID            = default_to_empty_string(commission["domainID"]),
                    merchantID          = default_to_empty_string(commission["merchantID"]),
                    publisherID         = default_to_empty_string(commission["publisherID"]),
                    items               = int(commission["items"]) if commission["items"] is not None else 0,
                    sales               = int(commission["sales"]) if commission["sales"] is not None else 0,
                    remoteReferer       = default_to_empty_string(commission["remoteReferer"]),
                    remoteUserAgent     = default_to_empty_string(commission["remoteUserAgent"]),
                    url                 = default_to_empty_string(commission["url"]),
                    domain              = default_to_empty_string(shorten_to_domain(commission["url"]) if commission["url"] else ""),
                    status              = default_to_empty_string(commission["status"])
                )
                comm.save()
            except:
                print json.dumps(commissions["skimlinksAccount"]["commissions"][c], indent=4)
                print_stack_trace()
            # if self.get(commissionID)

class Commission(models.Model):
    commissionID        = models.CharField(max_length=255, null=True, blank=True, db_index=True, unique=True)
    commissionType      = models.CharField(max_length=255, null=True, blank=True)
    commissionValue     = models.FloatField(default=0) #in dollars
    orderValue          = models.FloatField(default=0) #in dollars
    currency            = models.CharField(max_length=10, null=True, blank=True)
    customID            = models.CharField(max_length=50, null=True, blank=True)
    customIDAsInt       = models.IntegerField(max_length=50, null=True, blank=True)
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

    objects = CommissionManager()

    def save(self, *args, **kwargs):
        newly_created = False if self.id else True
        if self.customID:
            try:
                self.customIDAsInt = int(self.customID)
            except:
                pass
        super(Commission, self).save(*args, **kwargs)
        if newly_created:
            #attempt creating a RevenueVisitor object
            visitor_id = self.customIDAsInt
            if visitor_id and visitor_id > 0:
                if RevenueVisitor.objects.filter(visitor_id=visitor_id).count() == 0:
                    RevenueVisitor(visitor=Visitor.objects.get(id=visitor_id)).save()
