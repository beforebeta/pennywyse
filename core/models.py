from __future__ import unicode_literals
import os
import urllib
import datetime
import urlparse

from django.conf import settings
from django.db import models
from django.db.models.query_utils import Q
from django.template.defaultfilters import slugify
from django.core.paginator import Paginator
from core.util import print_stack_trace, get_first_google_image_result, get_description_tag_from_url
from tracking.commission.skimlinks import get_merchant_description


def get_descriptive_image(name):
    return get_first_google_image_result(name)

def get_directed_image(image_url):
    try:
        return "/s/image/%s" % urllib.quote_plus(image_url)
    except:
        return settings.DEFAULT_IMAGE

def get_description(model):
    if not model.directlink:
        if model.name:
            return model.name
        else:
            return ""
    return get_description_tag_from_url(model.directlink)

base_description = "PennyWyse | Hand Verified Coupon Codes"
icon_url = "http://pennywyse.com/static/img/fbog.png"

#######################################################################################################################
#
# Category
#
#######################################################################################################################

class Category(models.Model):
    ref_id          = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    code            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    name            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    description     = models.CharField(max_length=255,blank=True, null=True)
    parent          = models.ForeignKey("Category", blank=True, null=True)
    image           = models.TextField(blank=True, null=True)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(default=datetime.datetime.now(), auto_now=True, auto_now_add=True)

    def save(self, *args, **kwargs):
      if not self.image:
          self.image = get_descriptive_image(self.code)
      super(Category, self).save(*args, **kwargs)

    def get_coupons(self):
      return self.coupon_set.all().order_by("-created")

    def get_active_coupons(self):
        return self.coupon_set.all().filter(Q(end__gt=datetime.datetime.now()) | Q(end__isnull=True)).order_by("-created")

    def get_coupon_count(self):
      return self.get_active_coupons().count()

    def get_coupon_categories(self):
      return Category.objects.filter(
        coupon__id__in=self.get_active_coupons().values_list('id')).distinct().order_by('name')

    def coupons_in_categories(self, selected_categories):
      return Paginator(self.get_active_coupons().filter(
        Q(categories__id__in=selected_categories) | Q(categories__id__isnull=True)), 10)

    def display_name(self):
      return self.name

    def local_path(self):
      return "/categories/{0}/".format(self.code)

    def page_description(self):
      return "Coupons for {0} | {1}".format(self.name, base_description)

    def page_title(self):
      return "Coupons for {0} | {1}".format(self.name, base_description)

    def og_title(self):
      return "Coupons for {0}".format(self.name)

    def og_description(self):
      return "Hand Verified Coupon Codes for {0} from PennyWyse.".format(self.name)

    def og_image(self):
      return icon_url

    def og_url(self):
      return "{0}{1}".format(settings.BASE_URL_NO_APPENDED_SLASH, self.local_path())

    def __unicode__(self):  # Python 3: def __str__(self):
      return "%s %s" % (self.code, self.name)

#######################################################################################################################
#
# DealType
#
#######################################################################################################################

class DealType(models.Model):
    code            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    name            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    description     = models.CharField(max_length=255,blank=True, null=True)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(default=datetime.datetime.now(), auto_now=True, auto_now_add=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return "%s %s" % (self.code, self.name)

#######################################################################################################################
#
# Merchant
#
#######################################################################################################################

class MerchantManager(models.Manager):

    def get_popular_companies(self, how_many=8):
        return Merchant.objects.exclude(coupon__isnull=True)[:how_many]

class Merchant(models.Model):
    ref_id          = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    name            = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    name_slug       = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    image           = models.TextField(blank=True, null=True)

    description     = models.TextField(blank=True, null=True) #loaded from the target link
    coupon_count    = models.IntegerField(default=0)

    link            = models.TextField(blank=True, null=True)
    directlink      = models.TextField(blank=True, null=True)
    skimlinks       = models.TextField(blank=True, null=True)
    redirect        = models.NullBooleanField()

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(default=datetime.datetime.now(), auto_now=True, auto_now_add=True)

    objects = MerchantManager()

    def get_top_coupon(self):
        try:
            top_coupon = self.get_active_coupons().filter(short_desc__icontains="%").order_by("-created")
            if top_coupon:
                return top_coupon[0]
            else:
                top_coupon = self.get_active_coupons().filter(short_desc__icontains="$").order_by("-created")
                if top_coupon:
                    return top_coupon[0]
                else:
                    return list(self.get_active_coupons()[:1])[0]
        except:
            return ""

    def get_coupons(self):
        return self.coupon_set.all().order_by("-created")

    def get_active_coupons(self):
        return self.coupon_set.all().filter(Q(end__gt=datetime.datetime.now()) | Q(end__isnull=True)).order_by("-created")

    def get_coupon_categories(self):
        categories = set()
        for c in self.get_active_coupons():
            for cat in c.categories.all():
                categories.add(cat)
        categories = sorted(list(categories), key=lambda cat: cat.name)
        return categories

    def get_coupon_count(self):
        return self.get_active_coupons().count()

    def get_image(self):
        return get_directed_image(self.image)

    def refresh_coupon_count(self):
        self.coupon_count = self.get_coupon_count()
        self.save()

    def save(self, *args, **kwargs):
        if not self.image:
            if self.ref_id:
                try:
                    logo_path = "static/img/logos/%s.gif" % self.ref_id
                    with open(os.path.join(settings.BASE_DIR,logo_path)): pass
                    # logo exists
                    self.image = settings.BASE_URL_NO_APPENDED_SLASH + "/" + logo_path
                except:
                    try:
                        logo_path = "static/img/logos/%s.jpg" % self.ref_id
                        with open(os.path.join(settings.BASE_DIR,logo_path)): pass
                        # logo exists
                        self.image = settings.BASE_URL_NO_APPENDED_SLASH + "/" + logo_path
                    except:
                        self.image = get_descriptive_image(self.name + " logo")
        if not self.description:
            self.description = get_description(self)
        self.name_slug = slugify(self.name)
        super(Merchant, self).save(*args, **kwargs)

    def __unicode__(self):  # Python 3: def __str__(self):
        return "%s %s" % (self.ref_id, self.name)

    def skimlinks_description(self):
        skim_desc = get_merchant_description(self.name_slug)
        if skim_desc == None:
          skim_desc = self.description
        return skim_desc

    def featured_coupon(self):
        active = self.get_active_coupons().filter(Q(end__gt = datetime.datetime.now()) | Q(end = None))
        active_codes = active.exclude(code = None)
        featured = None

        #active w/code and in apparel
        for coupon in active_codes:
            if coupon.in_category('apparel'):
                featured = coupon

        #active w/code NOT in apparel
        if featured == None and active_codes.exists():
            featured = active_codes[0]

        #active in apparel W/O code
        if featured == None and active.exists():
            for coupon in active:
                if coupon.in_category('apparel'):
                    featured = coupon
            if featured == None:
                featured = codes[0]

        return featured

    def display_name(self):
      return self.name

    def local_path(self):
      return "/coupons/{0}/{1}/".format(self.name_slug, self.id)

    def page_description(self):
      return "Coupons for {0} | {1} | {2}".format(self.name, self.description, base_description)

    def page_title(self):
      return "Coupons for {0} | {1}".format(self.name, base_description)

    def og_title(self):
      return "Coupons for {0}".format(self.name)

    def og_description(self):
      return "{0} | Hand Verified Coupon Codes for {1} from PennyWyse.".format(self.description, self.name)

    def og_image(self):
      return "{0}{1}".format(settings.BASE_URL_NO_APPENDED_SLASH, self.get_image())

    def og_url(self):
      return "{0}{1}".format(settings.BASE_URL_NO_APPENDED_SLASH, self.local_path())

#######################################################################################################################
#
# CouponNetwork
#
#######################################################################################################################

class CouponNetwork(models.Model):
    name            = models.CharField(max_length=255, db_index=True, blank=True, null=True)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(default=datetime.datetime.now(), auto_now=True, auto_now_add=True)

#######################################################################################################################
#
# Country
#
#######################################################################################################################

class Country(models.Model):
    code            = models.CharField(max_length=255, db_index=True)
    name            = models.CharField(max_length=255, db_index=True)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(default=datetime.datetime.now(), auto_now=True, auto_now_add=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return "%s %s" % (self.code, self.name)

#######################################################################################################################
#
# Coupon
#
#######################################################################################################################

class CouponManager(models.Manager):
    def get_new_coupons(self,how_many=10):
        #TODO: Improve
        return self.all().order_by("-created")[:how_many]

    def get_popular_coupons(self, how_many=10):
        #TODO: Improve
        #find merchants that have coupons associated with them
        merchants = list(Merchant.objects.exclude(coupon__isnull=True)[:10])
        coupons_by_merchant = {}
        popular_coupons = []
        curr_merchant_idx = 0
        tries = 0
        while len(popular_coupons) < how_many:
            tries += 1
            if tries > how_many * 10:
                break
            if curr_merchant_idx == len(merchants):
                curr_merchant_idx = 0
            curr_merchant_id = merchants[curr_merchant_idx].id
            if curr_merchant_id not in coupons_by_merchant:
                coupons_by_merchant[curr_merchant_id] = list(Coupon.active_objects.filter(merchant_id=curr_merchant_id).order_by("-created")[:how_many])
            if len(coupons_by_merchant[curr_merchant_id]) > 0:
                popular_coupons.append(coupons_by_merchant[curr_merchant_id][0])
                coupons_by_merchant[curr_merchant_id] = coupons_by_merchant[curr_merchant_id][1:]
            curr_merchant_idx += 1
        return popular_coupons

class ActiveCouponManager(models.Manager):
    def get_query_set(self):
        return super(ActiveCouponManager, self).get_query_set().filter(Q(end__gt=datetime.datetime.now()) | Q(end__isnull=True))


class Coupon(models.Model):
    """
    CouponID - Our proprietary coupon ID - especially useful in identifying deals that are delivered more than once because they have changed.
    MerchantName
    MerchantID
    Network
    Label - The main description text the merchant describes the deal with. May be have been modified to fix typos.
    Restrictions - Any information the merchant provides regarding any restrictions relating to how the coupon can be redeemed. May have been modified to fix typos.
    CouponCode - If the coupon requires the user to enter a code, it is in this field. Any deal with a code will also contain "coupon" in the DealTypes field.
    StartDate
    EndDate
    Link - This is the actual affiliate link used to go to the merchant's landing page and set the appropriate network cookies with your affiliate info. It requires that you have inserted your affiliate IDs in the Feed Settings. NOTE: For deals marked "coupon" in the DealTypes field (below) this link may be required in order to activate the deal.
    DirectLink - This field is deprecated, please ignore it. It remains for backward compatibility.
    Categories        (Multiple values are seperatated by commas)
    DealTypes        (Multiple values are seperatated by commas)
    Image
    Status - The status should always be checked, and only "active" deals should be displayed (regardless of expiration date). The status is critical to tell if the deal is currently valid. Values may be: active - Deal is live and may be displayed; deleted - Deal was deleted or otherwise invalidated - ignore other values and remove deal; suspended - The merchant was deactivated in the network so this deal may not be paybale; or expired - The deal expired normally.
    LastUpdated - When this deal was last modified in the system.
    ErrorReportURL   (Optional, Turn on/off on Manage Feed Settings page)
    ChangeAudit      (Optional, Turn on/off on Manage Feed Settings page)
    Created      (When this deal was added to the system)
    Country      (Countries of the deal)
    Price      (Product Price, not applied to all deals)
    List Price      (Product List Price, not applied to all deals)
    Discount      (Product Discount, not applied to all deals)
    Percent      (Product Discount Percent, not applied to all deals)
    """
    #Our proprietary coupon ID - especially useful in identifying deals that are delivered more than once because they have changed.
    ref_id          = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    merchant        = models.ForeignKey(Merchant, blank=True, null=True)
    categories      = models.ManyToManyField(Category, blank=True, null=True)
    dealtypes       = models.ManyToManyField(DealType, blank=True, null=True)
    #The main description text the merchant describes the deal with. May be have been modified to fix typos.
    description     = models.TextField(blank=True, null=True)
    #Any information the merchant provides regarding any restrictions relating to how the coupon can be redeemed. May have been modified to fix typos.
    restrictions    = models.TextField(blank=True, null=True)
    #If the coupon requires the user to enter a code, it is in this field. Any deal with a code will also contain "coupon" in the DealTypes field.
    code            = models.CharField(max_length=255, blank=True, null=True)
    start           = models.DateTimeField(blank=True, null=True)
    end             = models.DateTimeField(blank=True, null=True)
    link            = models.TextField(blank=True, null=True)
    directlink      = models.TextField(blank=True, null=True)
    skimlinks       = models.TextField(blank=True, null=True)
    status          = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    lastupdated     = models.DateTimeField(blank=True, null=True)
    created         = models.DateTimeField(blank=True, null=True)
    countries       = models.ManyToManyField(Country, blank=True, null=True)
    price           = models.FloatField(default=0)
    listprice       = models.FloatField(default=0)
    discount        = models.FloatField(default=0)
    percent         = models.IntegerField(default=0)
    image           = models.TextField(blank=True, null=True)
    short_desc      = models.CharField(max_length=50, default="COUPON")

    desc_slug       = models.CharField(max_length=175, default="COUPON")

    embedly_title = models.TextField(blank=True, null=True)
    embedly_description = models.TextField(blank=True, null=True)
    embedly_image_url = models.TextField(blank=True, null=True)

    date_added      = models.DateTimeField(default=datetime.datetime.now(), auto_now_add=True)
    last_modified   = models.DateTimeField(default=datetime.datetime.now(), auto_now=True, auto_now_add=True)

    objects = models.Manager()
    active_objects = ActiveCouponManager()

    def get_image(self):
        if self.embedly_image_url:
            return get_directed_image(self.embedly_image_url)
        else:
            return get_directed_image(self.image)

    def get_description(self):
        if self.embedly_description:
            return self.embedly_description
        else:
            return self.description

    def has_deal_type(self, dealtype_code):
        return True if self.dealtypes.filter(code=dealtype_code).count()>0 else False

    def get_retailer_link(self):
        """retrieves the direct link to the page"""
        try:
            parsed = urlparse.urlparse(self.skimlinks)
            query = parsed.query.replace('&amp;','&')
            return urlparse.parse_qs(query)["url"][0]
        except:
            print_stack_trace()
            return self.skimlinks

    def create_short_desc(self):
        try:
            short = self.description.lower()
            if not short:
                return "coupon"
            arr = short.split(" ")

            try:
                if "% off" in short:
                    for i in range(len(arr)):
                        if arr[i].startswith("off"):
                            break
                    return " ".join([arr[i-1], "off"])
            except:
                pass

            try:
                if self.has_deal_type("percent"):
                    for i in range(len(arr)):
                        if arr[i].endswith("%"):
                            return "%s off" % arr[i]
            except:
                pass

            try:
                if self.has_deal_type("dollar"):
                    for i in range(len(arr)):
                        if arr[i].startswith("$"):
                            return "%s off" % arr[i]
            except:
                pass

            try:
                if self.discount and self.discount > 0:
                    return "$%s off" % int(self.discount)
            except:
                pass

            if self.has_deal_type("gift"):
                return "gift"

            if self.has_deal_type("sale"):
                return "sale"

            if self.has_deal_type("offer"):
                return "offer"

            if self.has_deal_type("freeshipping") or self.has_deal_type("totallyfreeshipping"):
                return "free ship"
        except:
            print self.ref_id, "Description is", self.description
            print_stack_trace()
        return "coupon"

    def create_image(self):
        if self.merchant:
            return self.merchant.image
#            if self.categories.count()>0:
#                if self.categories.exclude(name="apparel").count()>0:
#                    return self.categories.exclude(name="apparel")[0].image
#                else:
#                    return self.categories.all()[0].image
        return settings.DEFAULT_IMAGE

    def save(self, *args, **kwargs):
        if self.description:
            if self.description.endswith("."):
                self.description = self.description[:-1]
            #Hierarchy for setting short desc
            self.short_desc = self.create_short_desc()
            self.desc_slug = slugify(self.description)[:175]
        super(Coupon, self).save(*args, **kwargs)
        try:
            if not self.image:
                self.image = self.create_image()
            super(Coupon, self).save(*args, **kwargs)
        except:
            pass

    def __unicode__(self):  # Python 3: def __str__(self):
        if self.merchant:
            return "%s %s %s" % (self.merchant.name, self.ref_id, self.description)
        else:
            return "%s %s" % (self.ref_id, self.description)

    def in_category(self, category):
      return category in [c.code for c in self.categories.all()]

    def local_path(self):
      return "/coupons/{0}/{1}/{2}/".format(self.merchant.name_slug, self.desc_slug, self.id)

    def page_description(self):
      return "{0} | {1}".format(self.get_description(), self.merchant.page_description())

    def page_title(self):
      return "{0} | {1}".format(self.description, self.merchant.page_title())

    def og_title(self):
      return "{0}: {1}. A Hand Verified Coupon Code for {2} from PennyWyse.".format(self.merchant.name, self.description, self.merchant.name)

    def og_description(self):
      return "{0}: {1}. A Hand Verified Coupon Code for {2} from PennyWyse.".format(self.merchant.name, self.description, self.merchant.name)

    def og_image(self):
      return "{0}{1}".format(settings.BASE_URL_NO_APPENDED_SLASH, self.merchant.get_image())

    def og_url(self):
      return "{0}{1}".format(settings.BASE_URL_NO_APPENDED_SLASH, self.local_path())
