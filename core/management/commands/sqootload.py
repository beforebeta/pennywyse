import requests
import math

from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
# from django.conf import settings

from coupons.basesettings import SQOOT_PUBLIC_KEY
from core.models import DealType, Category, Coupon, Merchant, Country, CouponNetwork

## Need a scheduled task to delete expired deals?



class Command(BaseCommand):

    def handle(self, *args, **options):
        # err = self.stderr
        # out = self.stdout
        refresh_sqoot()


def section(message):
    print " "
    print "*"*60
    print message
    print "*"*60

def refresh_sqoot():
    parameters = {
        # 'api_key': settings.SQOOT_PUBLIC_KEY,
        'api_key': SQOOT_PUBLIC_KEY,
        'per_page': 1,
    }
    api_root = "http://api.sqoot.com/v2/"
    active_deal_count = requests.get(api_root + 'deals', params=parameters).json()['query']['total']
    page_count = int(math.ceil(active_deal_count / float(parameters['per_page'])))
    print "\n{} deals detected, estimating {} pages to iterate".format(active_deal_count, page_count)

    section("Start retrieving Sqoot data...")

    current_page_counter = 100
    # while True:
    while (current_page_counter < 10):
        parameters['page'] = current_page_counter

        print '\nFetching page {}...\n'.format(current_page_counter)
        response_in_json = requests.get(api_root + 'deals', params=parameters).json()
        deals_data_array = response_in_json['deals']

        if len(deals_data_array) == 0:
            print 'No more deals to retrieve from Sqoot. :('
            break

        for i in range(0, len(deals_data_array)):
            each_deal_data = deals_data_array[i]['deal']
            deal_merchant_data = each_deal_data['merchant']

            merchant_model = refresh_merchant(deal_merchant_data)


def refresh_merchant(merchant_data_dict):
    ref_id = merchant_data_dict['id']
    try:
        merchant_model = Merchant.objects.get(ref_id=ref_id, ref_id_source='sqoot')
    except:
        merchant_model = Merchant()

    merchant_model.ref_id           = ref_id
    merchant_model.ref_id_source    = "sqoot"
    merchant_model.name             = merchant_data_dict['name']
    merchant_model.link             = merchant_data_dict['url']
    merchant_model.directlink       = merchant_data_dict['url']
    merchant_model.skimlinks        = None
    merchant_model.save()
    return merchant_model




















