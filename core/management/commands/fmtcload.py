from optparse import make_option
from BeautifulSoup import BeautifulStoneSoup
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from core.models import DealType, Category, Coupon, Merchant, Country

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--load',
            action='store_true',
            dest='load',
            default=False,
            help='load'),
        )

    def handle(self, *args, **options):
        err = self.stderr
        out = self.stdout
        if options['load']:
            load()

def section(message):
    print " "
    print "*"*60
    print message
    print "*"*60

def refresh_deal_types():
    section("Loading Deal Types")
    data = requests.get("http://services.formetocoupon.com/getTypes?key=%s" % settings.FMTC_ACCESS_KEY)
    data = BeautifulStoneSoup(data.content)
    for type in data.findAll("type"):
        code = type.filter.text
        name = type.find("name").text
        DealType.objects.filter(code=code).delete()
        DealType(code=code,name=name,description=name).save()
        print "\t%s,%s" % (code,name)

def refresh_categories():
    section("Loading Categories")
    data = requests.get("http://services.formetocoupon.com/getCategories?key=%s" % settings.FMTC_ACCESS_KEY)
    data = BeautifulStoneSoup(data.content)
    for cat in data.findAll("category"):
        ref_id = cat.find("id").text
        code = cat.filter.text
        name = cat.find("name").text
        parent = cat.find("parent").text
        if parent:
            parent=Category.objects.get(code=parent)
        else:
            parent=None
        Category.objects.filter(code=code).delete()
        Category(ref_id=ref_id,code=code,name=name,parent=parent).save()
        print "\t%s,%s" % (code,name)

def get_dt(dt_str):
    if dt_str:
        dt = dt_str[:dt_str.rfind(" ")]
        if dt:
            return datetime.strptime(dt, "%Y-%m-%d %H:%M")
    return None

def refresh_deals():
    section("Loading Deals/Coupons")
    data = requests.get("http://services.formetocoupon.com/getDeals?key=%s" % settings.FMTC_ACCESS_KEY)
    data = BeautifulStoneSoup(data.content)
    for deal in data.findAll("item"):
        id = deal.couponid.text
        coupon=None
        try:
            coupon = Coupon.objects.get(ref_id = id)
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

        coupon.description = deal.label.text
        coupon.restrictions = deal.restrictions.text
        coupon.code = deal.couponcode.text

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

def load():
    refresh_deal_types()
    refresh_categories()
    refresh_deals()
