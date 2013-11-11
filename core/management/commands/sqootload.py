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
        refresh_sqoot_data()


def refresh_sqoot_data():
    request_parameters = {
        # 'api_key': settings.SQOOT_PUBLIC_KEY,
        'api_key': SQOOT_PUBLIC_KEY,
    }
    api_root = "http://api.sqoot.com/v2/"
    print "\nSqoot data load starting;\n"

    describe_section("Establshing category dict...\n")
    categories_array = requests.get(api_root + 'categories', params=request_parameters).json()['categories']
    categories_dict = establish_categories_dict(categories_array)

    describe_section("Checking the latest deal data...\n")
    request_parameters['per_page'] = 1
    active_deal_count = requests.get(api_root + 'deals', params=request_parameters).json()['query']['total']
    page_count = int(math.ceil(active_deal_count / float(request_parameters['per_page'])))
    print "{} deals detected, estimating {} pages to iterate\n".format(active_deal_count, page_count)

    describe_section("Start retrieving Sqoot data...\n")
    current_page_counter = 100
    # while True:
    while (current_page_counter < 10):
        request_parameters['page'] = current_page_counter

        print 'Fetching page {}...\n'.format(current_page_counter)
        response_in_json = requests.get(api_root + 'deals', params=request_parameters).json()
        deals_data_array = response_in_json['deals']

        if len(deals_data_array) == 0:
            print 'No more deals to retrieve from Sqoot. :('
            break

        for i in range(0, len(deals_data_array)):
            each_deal_data_dict = deals_data_array[i]['deal']
            merchant_data_dict = each_deal_data_dict['merchant']

            merchant_model = get_or_create_merchant(merchant_data_dict)
            category_model = get_or_create_category(each_deal_data_dict, categories_dict)


#############################################################################################################
#
# Helper Methods
#
#############################################################################################################

def establish_categories_dict(categories_array):
    categories_dict = {}
    for category in categories_array:
        category_slug = category['category']['slug']
        parent_slug = category['category']['parent_slug'] or None
        categories_dict[category_slug] = parent_slug
    category_count = len(categories_dict.keys())
    parent_count = len(filter(None, set(categories_dict.values())))
    print 'Category tree established with {} categories and {} parents.\n'.format(category_count, parent_count)
    return categories_dict

def get_or_create_merchant(merchant_data_dict):
    ref_id = merchant_data_dict['id']
    try:
        merchant_model = Merchant.objects.get(ref_id=ref_id, ref_id_source='sqoot')
    except:
        merchant_model                  = Merchant()
        merchant_model.ref_id           = ref_id
        merchant_model.ref_id_source    = "sqoot"

    merchant_model.name                 = merchant_data_dict['name']
    merchant_model.link                 = merchant_data_dict['url']
    merchant_model.directlink           = merchant_data_dict['url']
    merchant_model.skimlinks            = None
    merchant_model.save()
    return merchant_model

def get_or_create_category(each_deal_data_dict, categories_dict):
    category_slug = each_deal_data_dict['category_slug']
    parent_slug = categories_dict[category_slug]
    try:
        category_model = Category.objects.get(code=category_slug, ref_id_source='sqoot')
    except:
        category_model                    = Category()
        category_model.ref_id_source      = 'sqoot'
        category_model.code               = category_slug

    if parent_slug:
        try:
            parent_category               = Category.objects.get(code=parent_slug, ref_id_source='sqoot')
            category_model.parent         = parent_category
        except:
            parent_category               = Category()
            parent_category.ref_id_source = 'sqoot'
            parent_category.code          = parent_slug
            category_model.parent         = parent_category
    else:
        category_model.parent             = None

    category_model.name = each_deal_data_dict['category_name'] # In case it was already created as another category's parent
    category_model.save()
    return category_model

def describe_section(message):
    print " "
    print "*~"*30
    print message

