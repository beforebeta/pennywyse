from BeautifulSoup import BeautifulStoneSoup
import datetime
from lxml import etree
from optparse import make_option
from urlparse import urlparse, parse_qs

from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Category, Country, Coupon, DealType, Merchant, MerchantAffiliateData
from core.util import print_stack_trace
from web.models import FeaturedCoupon, NewCoupon, PopularCoupon
from websvcs.models import EmbedlyMerchant

import HTMLParser
import requests


IFRAME_DISALLOWED = ['eBay', 'eBay Canada']
DATETIME_FORMAT = '%b-%d-%I%M%p-%G'

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--load',
            action='store_true',
            dest='load',
            default=False,
            help='load'),
        make_option('--embedly',
            action='store_true',
            dest='embedly',
            default=False,
            help='embedly'),
        )

    def handle(self, *args, **options):
        err = self.stderr
        out = self.stdout
        if options['load']:
            load()
        if options['embedly']:
            embedly(args)

def section(message):
    print " "
    print "*"*60
    print message
    print "*"*60

def unescape_html(html):
    return HTMLParser.HTMLParser().unescape(html)

def _download_content(url, filename):
    print 'Downloading content from %s' % url
    r = requests.get(url, stream=True)
    with open(filename, 'w') as f:
        for c in r.iter_content(chunk_size=2048):
            if c:
                f.write(c)
                f.flush()
    return open(filename, 'r') 

def refresh_deal_types():
    section("Loading Deal Types")
    fh = _download_content("http://services.formetocoupon.com/getTypes?key=%s" % settings.FMTC_ACCESS_KEY,
                           "Deal_Types_Content_%s" % datetime.datetime.now().strftime(DATETIME_FORMAT))
    data = etree.iterparse(fh, tag='type')
    for event, deal_type in data:
        code = deal_type.find('filter').text
        name = deal_type.find("name").text
        print "\t%s,%s" % (code,name)
        if DealType.objects.filter(code=code).count() > 0:
            continue
        DealType.objects.filter(code=code).delete()
        DealType(code=code, name=name, description=name).save()

def refresh_categories():
    section("Loading Categories")
    fh = _download_content("http://services.formetocoupon.com/getCategories?key=%s" % settings.FMTC_ACCESS_KEY,
                           "Categories_Content_%s" % datetime.datetime.now().strftime(DATETIME_FORMAT))
    data = etree.iterparse(fh, tag='category')
    for event, cat in data:
        ref_id = cat.find("id").text
        code = unescape_html(cat.find('filter').text)
        name = unescape_html(cat.find("name").text)
        parent = cat.find("parent").text
        if parent:
            parent = Category.objects.get(code=parent)
        else:
            parent = None
        if Category.objects.filter(code=code).count() > 1:
            print "WARNING: Multiple categories with the same code: ", code
        existing_category, created = Category.objects.get_or_create(code=code)
        existing_category.ref_id = ref_id
        existing_category.name=name
        existing_category.parent=parent
        existing_category.save()
        print "\t%s,%s" % (code,name)

def refresh_merchants():
    section("Loading Merchants")
    fh = _download_content("http://services.formetocoupon.com/getMerchants?key=%s" % settings.FMTC_ACCESS_KEY,
                               "Merchants_Content_%s" % datetime.datetime.now().strftime(DATETIME_FORMAT))
    data = etree.iterparse(fh, tag='merchant')
    for event, merchant in data:
        try:
            name = unescape_html(merchant.find("name").text)
            id = merchant.find("id").text
            print "\t%s,%s" % (id,name)
            print '=' * 40
            link = merchant.find('link').text
            skimlinks = merchant.find('skimlinks').text
            homepageurl = merchant.find('homepageurl').text
            model, created = Merchant.objects.get_or_create(name=name)
            model.directlink = homepageurl
            model.skimlinks = skimlinks
            model.link = homepageurl
            model.save()
            affiliate_data, created = MerchantAffiliateData.objects.get_or_create(ref_id=id, merchant=model)
            affiliate_data.network = merchant.find('network').text
            affiliate_data.networkid = merchant.find('networkid').text
            affiliate_data.networknote = merchant.find('networknote').text
            affiliate_data.link = link
            if merchant.find('network').text == 'CJ':
                affiliate_data.primary = True
            affiliate_data.save()
        except:
            print_stack_trace()


def get_dt(dt_str):
    if dt_str:
        dt = dt_str[:dt_str.rfind(" ")]
        if dt:
            return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")
    return None

def refresh_deals():
    section("Loading Deals/Coupons")
    fh = _download_content("http://services.formetocoupon.com/getDeals?key=%s" % settings.FMTC_ACCESS_KEY,
                           "Deals_Content_%s" % datetime.datetime.now().strftime(DATETIME_FORMAT))
    data = etree.iterparse(fh, tag='item')
    for event, deal in data:
        try:
            id = deal.find('couponid').text
            coupon, created = Coupon.active_objects.get_or_create(ref_id=id)

            merchant_name = deal.find('merchantname').text
            merchantid = deal.find('merchantid').text
            merchant, created = Merchant.objects.get_or_create(name=merchant_name)
            coupon.merchant=merchant

            coupon.categories.clear()
            for category in deal.findall("category"):
                coupon.categories.add(Category.objects.get(code=category.text))

            coupon.dealtypes.clear()
            dealtypes = deal.find('dealtypes')
            for dealtype in dealtypes.findall("type"):
                coupon.dealtypes.add(DealType.objects.get(code=dealtype.text))

            coupon.description = unescape_html(deal.find('label').text)
            restrictions = deal.find('restrictions').text or ''
            coupon.restrictions = unescape_html(restrictions)
            coupon_code = deal.find('couponcode').text or ''
            coupon.code = unescape_html(coupon_code)

            coupon.start = get_dt(deal.find('startdate').text)
            coupon.end = get_dt(deal.find('enddate').text)
            coupon.lastupdated = get_dt(deal.find('lastupdated').text)
            coupon.created = get_dt(deal.find('created').text)
            coupon.link = deal.find('link').text
            
            # removing skimlinks prefix from coupon link
            parsed_link = urlparse(deal.find('link').text)
            if str(parsed_link.netloc) == 'go.redirectingat.com':
                qs = parse_qs(parsed_link.query)
                coupon_link = qs.get('url')
                if coupon_link:
                    coupon.link = coupon_link[0]
            
            coupon.directlink = deal.find('directlink').text
            coupon.skimlinks = deal.find('skimlinks').text
            coupon.status = deal.find('status').text

            coupon.countries.clear()

            for country in deal.findall("country"):
                c, created = Country.objects.get_or_create(code=country.text)
                c.name = country.text
                c.save()
                coupon.countries.add(c)

            coupon.price = deal.find('price').text
            coupon.discount = deal.find('discount').text
            coupon.listprice = deal.find('listprice').text
            coupon.percent = deal.find('percent').text
            coupon.image = deal.find('image').text
            coupon.save()
        except:
            print_stack_trace()

def setup_web_coupons():
    section("Setup Web Coupons")
    try:
        if Coupon.objects.filter(is_featured=True).count() == 0:
            for name in ['best buy', 'sears', 'target']:
                coupon = Merchant.objects.get(name=name).get_top_coupon()
                coupon.is_featured = True
                coupon.save()
    except:
        print_stack_trace()

    try:
        if Coupon.objects.filter(is_new=True).count() == 0:
            for coupon in Coupon.active_objects.get_new_coupons(8):
                coupon.is_new = True
                coupon.save()
    except:
        print_stack_trace()

    try:
        if Coupon.objects.filter(is_popular=True).count() == 0:
            for coupon in Coupon.active_objects.get_popular_coupons(8):
                coupon.is_popular = True
                coupon.save()
    except:
        print_stack_trace()

def refresh_calculated_fields():
    section("Refresh Calculated Fields")
    for m in Merchant.objects.all():
        try:
            m.refresh_coupon_count()
        except:
            print "Error with: ", m.name, m.id
            print_stack_trace()

def refresh_merchant_redirects():
    for coupon in Coupon.objects.all():
        if coupon.link and not coupon.merchant.redirect:
            try:
                request = requests.get(coupon.link, timeout=20)
                if request.headers.get('x-frame-options', False) == 'SAMEORIGIN':
                    coupon.merchant.redirect = True
                    coupon.merchant.save()
                    print "{0}: True!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".format(coupon.merchant.name)
                else:
                    print "{0}: False".format(coupon.merchant.name)
            except:
                print "{0} timed out connecting to {1}".format(coupon.merchant.name, coupon.link)
        else:
            print "{0}: else False".format(coupon.merchant.name)

    for merchant_name in IFRAME_DISALLOWED:
        Merchant.objects.filter(name=merchant_name).update(redirect=True)

def load():
    refresh_deal_types()
    refresh_categories()
    refresh_merchants()
    refresh_deals()
    setup_web_coupons()
    refresh_calculated_fields()
    refresh_merchant_redirects()

def embedly(args):
    _from = 0
    _to = Merchant.objects.all().count()
    if len(args) == 2:
        _from = int(args[0])
        _to = int(args[1])
        if _to == 1:
            _to = Merchant.objects.all().count()
    print "loading from", _from, "to", _to
    for merchant in Merchant.objects.all()[_from:_to]:
        try:
            EmbedlyMerchant(merchant).update_coupons()
        except:
            print_stack_trace()
