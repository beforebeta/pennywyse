# -*- coding: utf-8 -*-
import requests
import math
import datetime

from django.utils.html import strip_tags
from django.core.management.base import BaseCommand
from django.conf import settings

from core.models import DealType, Category, Coupon, Merchant, Country, CouponNetwork, MerchantLocation

# from coupons.basesettings import SQOOT_PUBLIC_KEY
from core.util import print_stack_trace


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            refresh_sqoot_data()
        except:
            print_stack_trace()


def refresh_sqoot_data():
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
        # 'api_key': SQOOT_PUBLIC_KEY,
    }
    api_root = "http://api.sqoot.com/v2/"
    print "\nSQOOT DATA LOAD STARTING..\n"

    describe_section("ESTABLISHING CATEGORY DISCTIONARY..\n")
    categories_array = requests.get(api_root + 'categories', params=request_parameters).json()['categories']
    categories_dict = establish_categories_dict(categories_array)

    describe_section("CHECKING THE LATEST DEAL DATA FROM SQOOT..\n")
    request_parameters['per_page'] = 100
    active_deal_count = requests.get(api_root + 'deals', params=request_parameters).json()['query']['total']
    page_count = int(math.ceil(active_deal_count / float(request_parameters['per_page'])))
    try:
        print "{} deals detected, estimating {} pages to iterate\n".format(active_deal_count, page_count)
    except:
        pass
    describe_section("STARTING TO DOWNLOAD SQOOT DEALS..\n")
    current_page_counter = 30
    deal_download_counter = 0
    while True:
        try:
            request_parameters['page'] = current_page_counter
            try:
                print '## Fetching page {}...\n'.format(current_page_counter)
            except:
                pass
            response_in_json = requests.get(api_root + 'deals', params=request_parameters).json()
            deals_data_array = response_in_json['deals']

            if len(deals_data_array) == 0:
                print 'No more deals to retrieve from Sqoot. :('
                break

            for i in range(0, len(deals_data_array)):
                try:
                    each_deal_data_dict = deals_data_array[i]['deal']
                    is_online_bool = each_deal_data_dict['online']
                    merchant_data_dict = each_deal_data_dict['merchant']

                    merchant_model          = get_or_create_merchant(merchant_data_dict)
                    category_model          = get_or_create_category(each_deal_data_dict, categories_dict)
                    dealtype_model          = get_or_create_dealtype()
                    country_model           = get_or_create_country()
                    couponnetwork_model     = get_or_create_couponnetwork(each_deal_data_dict)
                    merchantlocation_model  = get_or_create_merchantlocation(merchant_data_dict, merchant_model, is_online_bool)
                    get_or_create_coupon(each_deal_data_dict, merchant_model, category_model, dealtype_model, country_model, couponnetwork_model, merchantlocation_model)

                    deal_download_counter += 1
                    try:
                        print "...total of {} deals saved so far\n".format(deal_download_counter)
                    except:
                        pass
                except:
                    print_stack_trace()
        except:
            print_stack_trace()
        current_page_counter += 1
        if current_page_counter > 100:
            break

#############################################################################################################
#
# Helper Methods - Data
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
    try:
        print 'Category tree established with {} categories and {} parents.\n'.format(category_count, parent_count)
    except:
        pass
    return categories_dict

def get_or_create_merchant(merchant_data_dict):
    try:
        print "\t...get_or_create a merchant: {}".format(merchant_data_dict['name'])
    except:
        pass
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
    try:
        print "\t...get_or_create a category: {}".format(each_deal_data_dict['category_slug'])
    except:
        pass
    category_slug = each_deal_data_dict['category_slug']
    if not category_slug:
        return None
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
            parent_category.save()
            category_model.parent         = parent_category
    else:
        category_model.parent             = None

    # In case it was already created as another category's parent (hence save outside try-except)
    category_model.name = each_deal_data_dict['category_name']
    category_model.save()
    return category_model

def get_or_create_dealtype():
    '''
    Treat all deals from sqoot as 'local' deals.
    '''
    print "\t...get_or_create a dealtype"

    try:
        dealtype_model      = DealType.objects.get(code='local')
    except:
        dealtype_model      = DealType()
        dealtype_model.code = 'local'
        dealtype_model.name = 'Local'
        dealtype_model.save()
    return dealtype_model

def get_or_create_country():
    '''
    All deals from sqoot are US deals for now
    (They say they are going to add international deals at some point)
    '''
    print "\t...get_or_create a country"
    try:
        country_model      = Country.objects.get(code='usa')
    except:
        country_model      = Country()
        country_model.code = 'usa'
        country_model.name = 'usa'
        country_model.save()
    return country_model

def get_or_create_couponnetwork(each_deal_data_dict):
    print "\t...get_or_create a coupon_network"
    provider_slug = each_deal_data_dict['provider_slug']
    try:
        couponnetwork_model      = CouponNetwork.objects.get(code=provider_slug)
    except:
        couponnetwork_model      = CouponNetwork()
        couponnetwork_model.code = provider_slug
        couponnetwork_model.name = each_deal_data_dict['provider_name']
        couponnetwork_model.save()
    return couponnetwork_model

def get_or_create_merchantlocation(merchant_data_dict, merchant_model, is_online_bool):
    '''
    If it's an online deal or lat/long data aren't available, this function does nothing.
    '''
    print "\t...get_or_create a merchant_location"
    longitude = merchant_data_dict['longitude']
    latitude = merchant_data_dict['latitude']
    point_wkt = 'POINT({} {})'.format(longitude, latitude)

    if is_online_bool == True or longitude == None or latitude == None:
        return
    else:
        try:
            merchantlocation_model = MerchantLocation.objects.get(geometry__equals = point_wkt, merchant = merchant_model)
        except:
            merchantlocation_model              = MerchantLocation()
            merchantlocation_model.merchant     = merchant_model
            merchantlocation_model.geometry     = point_wkt
            merchantlocation_model.address      = merchant_data_dict['address']
            merchantlocation_model.locality     = merchant_data_dict['locality']
            merchantlocation_model.region       = merchant_data_dict['region']
            merchantlocation_model.postal_code  = merchant_data_dict['postal_code']
            merchantlocation_model.country      = merchant_data_dict['country']
            merchantlocation_model.save()
        return merchantlocation_model

def get_or_create_coupon(each_deal_data_dict, merchant_model, category_model, dealtype_model, country_model, couponnetwork_model, merchantlocation_model):
    try:
        print "\t...get_or_create a coupon: ID({})-{}".format(each_deal_data_dict['id'], each_deal_data_dict['title'])
    except:
        pass
    ref_id = each_deal_data_dict['id']
    try:
        coupon_model                     = Coupon.objects.get(ref_id=ref_id, ref_id_source='sqoot')
    except:
        coupon_model                     = Coupon()
        coupon_model.ref_id              = ref_id
        coupon_model.ref_id_source       = 'sqoot'
        coupon_model.online              = each_deal_data_dict['online']
        coupon_model.merchant            = merchant_model
        coupon_model.merchant_location   = merchantlocation_model
        coupon_model.description         = strip_tags(each_deal_data_dict['description'])
        coupon_model.restrictions        = strip_tags(each_deal_data_dict['fine_print'])
        coupon_model.start               = get_date(each_deal_data_dict['created_at'])
        coupon_model.end                 = get_date(each_deal_data_dict['expires_at'])
        coupon_model.link                = each_deal_data_dict['url']
        coupon_model.directlink          = each_deal_data_dict['untracked_url']
        coupon_model.skimlinks           = each_deal_data_dict['url']
        coupon_model.status              = 'active'
        coupon_model.lastupdated         = get_date(each_deal_data_dict['updated_at'])
        coupon_model.created             = get_date(each_deal_data_dict['created_at'])
        coupon_model.coupon_network      = couponnetwork_model
        coupon_model.price               = each_deal_data_dict['price']
        coupon_model.listprice           = each_deal_data_dict['value']
        coupon_model.discount            = each_deal_data_dict['discount_amount']
        coupon_model.percent             = int(each_deal_data_dict['discount_percentage'] * 100)
        coupon_model.image               = each_deal_data_dict['image_url']
        coupon_model.embedly_title       = each_deal_data_dict['title']
        coupon_model.embedly_description = each_deal_data_dict['short_title']
        coupon_model.embedly_image_url   = each_deal_data_dict['image_url']
        coupon_model.save()

        if category_model:
            categories = []
            categories.append(category_model)
            while category_model.parent:
                categories.append(category_model.parent)
                category_model = category_model.parent
            for cat in categories:
                coupon_model.categories.add(cat)
        coupon_model.dealtypes.add(dealtype_model)
        coupon_model.countries.add(country_model)
        coupon_model.save()
    print "\t~~~all deal related data saved!"


#############################################################################################################
#
# Helper Methods - Formatting
#
#############################################################################################################

def describe_section(message):
    print " "
    print "*~"*30
    print message

def get_date(raw_date_string):
    if raw_date_string:
        clean_date_string = raw_date_string[:-4].replace('T', ' ')
        return datetime.datetime.strptime(clean_date_string, "%Y-%m-%d %H:%M")
    return None
