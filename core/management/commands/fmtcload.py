from optparse import make_option
from BeautifulSoup import BeautifulStoneSoup
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from core.models import DealType, Category, Coupon, Merchant, Country
from core.util import print_stack_trace
from web.models import FeaturedCoupon, NewCoupon, PopularCoupon
from websvcs.models import EmbedlyMerchant
import HTMLParser

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

def refresh_deal_types():
    section("Loading Deal Types")
    data = requests.get("http://services.formetocoupon.com/getTypes?key=%s" % settings.FMTC_ACCESS_KEY)
    content = data.content
    open("Deal_Types_Content_%s" % datetime.datetime.now().strftime('%b-%d-%I%M%p-%G'), "w").write(content)
    data = BeautifulStoneSoup(content)
    for type in data.findAll("type"):
        code = type.filter.text
        name = type.find("name").text
        print "\t%s,%s" % (code,name)
        if DealType.objects.filter(code=code).count() > 0:
            continue
        DealType.objects.filter(code=code).delete()
        DealType(code=code,name=name,description=name).save()

def refresh_categories():
    section("Loading Categories")
    data = requests.get("http://services.formetocoupon.com/getCategories?key=%s" % settings.FMTC_ACCESS_KEY)
    content = data.content
    open("Categories_Content_%s" % datetime.datetime.now().strftime('%b-%d-%I%M%p-%G'), "w").write(content)
    data = BeautifulStoneSoup(content)
    for cat in data.findAll("category"):
        ref_id = cat.find("id").text
        code = unescape_html(cat.filter.text)
        name = unescape_html(cat.find("name").text)
        parent = cat.find("parent").text
        if parent:
            parent=Category.objects.get(code=parent)
        else:
            parent=None
        if Category.objects.filter(code=code).count() > 1:
            print "WARNING: Multiple categories with the same code: ", code
        try:
            existing_category = Category.objects.get(code=code)
            existing_category.ref_id = ref_id
            existing_category.name=name
            existing_category.parent=parent
            existing_category.save()
        except:
            Category(ref_id=ref_id,code=code,name=name,parent=parent).save()
        print "\t%s,%s" % (code,name)

def refresh_merchants():
    section("Loading Merchants")
    data = requests.get("http://services.formetocoupon.com/getMerchants?key=%s" % settings.FMTC_ACCESS_KEY)
    content = data.content
    open("Merchants_Content_%s" % datetime.datetime.now().strftime('%b-%d-%I%M%p-%G'), "w").write(content)
    data = BeautifulStoneSoup(content)
    for merchant in data.findAll("merchant"):
        try:
            name = unescape_html(merchant.find("name").text)
            id = merchant.find("id").text
            print "\t%s,%s" % (id,name)
            link = merchant.link.text
            skimlinks = merchant.skimlinks.text
            homepageurl = merchant.homepageurl.text
            model = None
            try:
                model = Merchant.objects.get(ref_id = id)
            except:
                model = Merchant()
            model.ref_id = id
            model.name = name
            model.directlink = homepageurl
            model.skimlinks = skimlinks
            model.link = homepageurl
            model.save()
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
    data = requests.get("http://services.formetocoupon.com/getDeals?key=%s" % settings.FMTC_ACCESS_KEY)
    content = data.content
    open("Deals_Content_%s" % datetime.datetime.now().strftime('%b-%d-%I%M%p-%G'), "w").write(content)
    data = BeautifulStoneSoup(content)
    for deal in data.findAll("item"):
        try:
            id = deal.couponid.text
            coupon=None
            try:
                coupon = Coupon.active_objects.get(ref_id = id)
            except:
                coupon=Coupon(ref_id=id)
                coupon.save()

            merchant_name = deal.merchantname.text
            merchantid = deal.merchantid.text
            merchant=None

            try:
                merchant = Merchant.objects.get(ref_id=merchantid)
            except:
                merchant=Merchant(ref_id=merchantid, name=merchant_name)
                merchant.save()
            coupon.merchant=merchant

            coupon.categories.clear()
            for category in deal.findAll("category"):
                coupon.categories.add(Category.objects.get(code=category.text))

            coupon.dealtypes.clear()
            for dealtype in deal.dealtypes.findAll("type"):
                coupon.dealtypes.add(DealType.objects.get(code=dealtype.text))

            coupon.description = unescape_html(deal.label.text)
            coupon.restrictions = unescape_html(deal.restrictions.text)
            coupon.code = unescape_html(deal.couponcode.text)

            coupon.start = get_dt(deal.startdate.text)
            coupon.end = get_dt(deal.enddate.text)
            coupon.lastupdated = get_dt(deal.lastupdated.text)
            coupon.created = get_dt(deal.created.text)

            coupon.link = deal.link.text
            coupon.directlink = deal.directlink.text
            coupon.skimlinks = deal.skimlinks.text
            coupon.status = deal.status.text

            coupon.countries.clear()

            for country in deal.findAll("country"):
                c=None
                try:
                    c=Country.objects.get(code=country.text)
                except:
                    c=Country(code=country.text,name=country.text)
                    c.save()
                coupon.countries.add(c)

            coupon.price = deal.price.text
            coupon.discount = deal.discount.text
            coupon.listprice = deal.listprice.text
            coupon.percent = deal.percent.text

            coupon.image = deal.image.text

            coupon.save()
        except:
            print_stack_trace()

def setup_web_coupons():
    section("Setup Web Coupons")
    try:
        if FeaturedCoupon.objects.all().count()<=0:
            FeaturedCoupon(coupon=Merchant.objects.get(name="best buy").get_top_coupon()).save()
            FeaturedCoupon(coupon=Merchant.objects.get(name="sears").get_top_coupon()).save()
            FeaturedCoupon(coupon=Merchant.objects.get(name="target").get_top_coupon()).save()
    except:
        print_stack_trace()

    try:
        if NewCoupon.objects.all().count()<=0:
            for coupon in Coupon.active_objects.get_new_coupons(8):
                NewCoupon(coupon=coupon).save()
    except:
        print_stack_trace()

    try:
        if PopularCoupon.objects.all().count()<=0:
            for coupon in Coupon.active_objects.get_popular_coupons(8):
                PopularCoupon(coupon=coupon).save()
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
