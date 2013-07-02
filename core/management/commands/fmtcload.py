from optparse import make_option
from BeautifulSoup import BeautifulStoneSoup
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from core.models import DealType, Category, Coupon

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
        DealType.objects.filter(code=code)
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

def refresh_deals():
    """
        <couponid>767400</couponid>
        <merchantname>Amazon</merchantname>
        <merchantid>2</merchantid>
        <network>AM</network>
        <programid></programid>
        <label>Grocery Sales and Special Offers.</label>
        <restrictions></restrictions>
        <couponcode></couponcode>
        <startdate>2010-05-25 0:00 PST</startdate>
        <enddate></enddate>
        <link>http://www.amazon.com/gp/redirect.html?ie=UTF8&amp;location=http%3A%2F%2Fwww.amazon.com%2FSales-Grocery%2Fb%3Fie%3DUTF8%26node%3D52129011%26ref_%3Damb%5Flink%5F353229922%5F2&amp;tag=ACTID&amp;linkCode=ur2&amp;camp=1789&amp;creative=390957</link>
        <directlink>http://www.amazon.com/Sales-Grocery/b?ie=UTF8&amp;node=52129011&amp;ref_=amb_link_353229922_2</directlink>
        <skimlinks>http://go.redirectingat.com/?id=52221X1268873&amp;xs=1&amp;xcust=formetocoupon&amp;url=http%3A%2F%2Fwww.amazon.com%2FSales-Grocery%2Fb%3Fie%3DUTF8%26node%3D52129011%26ref_%3Damb_link_353229922_2</skimlinks>
        <categories>
            <category>food-cooking</category>
            <category>online-grocery</category>
        </categories>
        <dealtypes>
            <type>coupon</type>
            <type>rebates</type>
            <type>category-coupon</type>
        </dealtypes>
        <image></image>
        <status>active</status>
        <lastupdated>2012-08-18 20:00 PST</lastupdated>
        <created>2010-05-25 11:15 PST</created>
        <countries>
            <country>usa</country>
        </countries>
        <price>0.00</price>
        <listprice>0.00</listprice>
        <discount>0.00</discount>
        <percent>0</percent>
    """
    section("Loading Deals/Coupons")
    data = requests.get("http://services.formetocoupon.com/getDeals?key=%s" % settings.FMTC_ACCESS_KEY)
    data = BeautifulStoneSoup(data.content)
    for deal in data.findAll("item"):
        id = deal.couponid.text
        Coupon.objects.filter(ref_id = id).delete()


def load():
    refresh_deal_types()
    refresh_categories()
    refresh_deals()
