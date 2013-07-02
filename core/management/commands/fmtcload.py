from optparse import make_option
from BeautifulSoup import BeautifulStoneSoup
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from core.models import DealType, Category

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
        Category.objects.filter(code=code).delete()
        Category(ref_id=ref_id,code=code,name=name,parent=Category.objects.get(code=parent)).save()
        print "\t%s,%s" % (code,name)

def load():
    refresh_deal_types()