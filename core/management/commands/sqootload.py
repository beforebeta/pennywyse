# -*- coding: utf-8 -*-
import datetime
import math
import requests
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.html import strip_tags
from django.db.models import Q

from BeautifulSoup import BeautifulSoup

from core.models import DealType, Category, Coupon, Merchant, Country, CouponNetwork, MerchantLocation
from tests.for_api.sample_data_feed import top_50_us_cities_dict
from core.util import print_stack_trace
import json

SQOOT_API_URL = "http://api.sqoot.com/v2/"
ITEMS_PER_PAGE = 100
SAVED_MERCHANT_ID_LIST = [int(m.ref_id) for m in Merchant.all_objects.filter(ref_id_source='sqoot')]

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--directload',
            action='store_true',
            dest='directload',
            default=False,
            help='directload'),
        make_option('--indirectload',
            action='store_true',
            dest='indirectload',
            default=False,
            help='indirectload'),
        make_option('--savedown',
            action='store_true',
            dest='savedown',
            default=False,
            help='savedown'),
        make_option('--validate',
            action='store_true',
            dest='validate',
            default=False,
            help='validate'),
        make_option('--analyze',
            action='store_true',
            dest='analyze',
            default=False,
            help='analyze'),
        )

    def handle(self, *args, **options):
        if options['directload']:
            try:
                refresh_sqoot_data()
            except:
                print_stack_trace()
        if options['indirectload']:
            try:
                refresh_sqoot_data(True)
            except:
                print_stack_trace()
        if options['savedown']:
            try:
                savedown_sqoot_data()
            except:
                print_stack_trace()
        if options['validate']:
            try:
                validate_sqoot_deals()
            except:
                print_stack_trace()
        if options['analyze']:
            try:
                analyze_sqoot_deals()
            except:
                print_stack_trace()

def refresh_sqoot_data(indirectload=False):
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
        # 'api_key': 'xhtihz',
    }
    print "\nSQOOT DATA LOAD STARTING..\n"

    # loading categories
    describe_section("ESTABLISHING CATEGORY DICTIONARY..\n")
    categories_array = requests.get(SQOOT_API_URL + 'categories', params=request_parameters).json()['categories']
    categories_dict = establish_categories_dict(categories_array)
    reorganized_categories_array = reorganize_categories_list(categories_array)
    for category_dict in reorganized_categories_array:
        get_or_create_category(category_dict, categories_dict)

    # loading coupons and merchants
    describe_section("CHECKING THE LATEST DEAL DATA FROM SQOOT..\n")
    request_parameters['per_page'] = ITEMS_PER_PAGE
    active_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['query']['total']
    page_count = int(math.ceil(active_deal_count / float(request_parameters['per_page'])))

    print '%s deals detected, estimating %s pages to iterate\n' % (active_deal_count, page_count)

    describe_section("STARTING TO DOWNLOAD SQOOT DEALS..\n")

    country_model = get_or_create_country()     # since there's only one country for all deals - no need to check it for each coupon
    sqoot_output_deals = None
    if indirectload:
        sqoot_output_deals = json.loads(open("sqoot_output.json","r").read())
    for p in range(page_count):
        request_parameters['page'] = p + 1
        print '## Fetching page %s...\n' % (p + 1)
        if indirectload:
            response_in_json = sqoot_output_deals[p]
        else:
            response_in_json = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()
        deals_data = response_in_json['deals']

        for deal_data in deals_data:
            try:
                is_online_bool = deal_data['deal']['online']
                merchant_data_dict = deal_data['deal']['merchant']

                merchant_model          = get_or_create_merchant(merchant_data_dict)
                category_model          = get_or_create_category(deal_data['deal'], categories_dict)
                dealtype_model          = get_or_create_dealtype()
                couponnetwork_model     = get_or_create_couponnetwork(deal_data['deal'])
                merchantlocation_model  = get_or_create_merchantlocation(merchant_data_dict, merchant_model, is_online_bool)
                coupon_model            = get_or_create_coupon(deal_data['deal'], merchant_model, category_model, dealtype_model,
                                                                country_model, couponnetwork_model, merchantlocation_model)

                coupon_ref_id = int(coupon_model.merchant.ref_id)
                if coupon_ref_id not in SAVED_MERCHANT_ID_LIST:
                    SAVED_MERCHANT_ID_LIST.append(coupon_ref_id)
                else:
                    check_and_mark_duplicate(coupon_model)

                print '-' * 60
            except:
                print_stack_trace()

def savedown_sqoot_data():
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
    }
    print "\nSQOOT DATA LOAD STARTING..\n"

    categories_array = requests.get(SQOOT_API_URL + 'categories', params=request_parameters).json()['categories']
    categories_dict = establish_categories_dict(categories_array)
    reorganized_categories_array = reorganize_categories_list(categories_array)
    for category_dict in reorganized_categories_array:
        get_or_create_category(category_dict, categories_dict)

    # loading coupons and merchants
    describe_section("CHECKING THE LATEST DEAL DATA FROM SQOOT..\n")
    request_parameters['per_page'] = ITEMS_PER_PAGE
    active_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['query']['total']
    page_count = int(math.ceil(active_deal_count / float(request_parameters['per_page'])))

    print '%s deals detected, estimating %s pages to iterate\n' % (active_deal_count, page_count)

    describe_section("STARTING TO DOWNLOAD SQOOT DEALS..\n")

    sqoot_file = open("sqoot_output.json", "w")
    sqoot_file.write("[")
    for p in range(page_count):
        request_parameters['page'] = p + 1
        print '## Fetching page %s...\n' % (p + 1)
        response_in_json = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()
        sqoot_file.write(json.dumps(response_in_json))
        sqoot_file.write(",")
    sqoot_file.write("]")
    sqoot_file.flush()
    sqoot_file.close()

def validate_sqoot_deals():
    suspicious_deals = Coupon.all_objects.filter(ref_id_source='sqoot', end__isnull=True)\
                                         .filter(Q(status='considered-active')| Q(status='unconfirmed'))
    for c in suspicious_deals:
        check_if_deal_gone(c)

def analyze_sqoot_deals():
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
    }

    # describe_section("Retrieving the latest categories..\n")
    # categories_array = requests.get(SQOOT_API_URL + 'categories', params=request_parameters).json()['categories']
    # category_slugs = [c['category']['slug'] for c in categories_array]

    describe_section("Retrieving the latest providers..\n")
    providers_array = requests.get(SQOOT_API_URL + 'providers', params=request_parameters).json()['providers']
    provider_slugs = [c['provider']['slug'] for c in providers_array]

    describe_section("Importing the latest 50 US cities..\n")
    target_cities = top_50_us_cities_dict

    describe_section("Checking total sqoot deals available..\n")
    total_deals_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['query']['total']

    TARGET_RADIUS = 50 # miles
    request_parameters['radius'] = TARGET_RADIUS
    describe_section("Checking sqoot deals currently available in {} mi radius of the following cities..\n".format(TARGET_RADIUS))
    for city in target_cities:
        request_parameters['location'] = target_cities[city]
        per_city_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['query']['total']
        print city, ': ', per_city_deal_count
    print 'total sqoot deal count: ', total_deals_count

    del request_parameters['location']

    describe_section("Preparing to check deal availablity from the following providers..\n")
    for p in provider_slugs:
        print p

    for p in provider_slugs:
        request_parameters['provider_slugs'] = p
        per_p_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['query']['total']
        if per_p_deal_count < 100:
            print "total deals available from {} too small: {}".format(p, per_p_deal_count)
            print "Skipping.."
            continue
        else:
            describe_section("Checking deals from {} for each city..\n".format(p))

        for city in target_cities:
            request_parameters['location'] = target_cities[city]
            per_city_and_p_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['query']['total']
            print city, ': ', per_city_and_p_deal_count
        print 'total {} deal count:  {}'.format(p, per_p_deal_count)
        del request_parameters['location']


#############################################################################################################
#
# Helper Methods - Data
#
#############################################################################################################

def reorganize_categories_list(categories_array):
    '''Manual renaming of "Retail & Services" to "Shopping & Services"'''
    categories_list = []
    for category in categories_array:
        category_name = category['category']['name']
        category_name = 'Shopping & Services' if category_name == 'Retail & Services' else category_name
        category_slug = category['category']['slug']
        category_slug = 'shopping-services' if category_slug == 'retail-services' else category_slug
        category_dict = {'category_name': category_name,
                         'category_slug': category_slug}
        categories_list.append(category_dict)
    return categories_list

def establish_categories_dict(categories_array):
    '''Manual renaming of "Retail & Services" to "Shopping & Services"'''
    categories_dict = {}
    for category in categories_array:
        category_slug = category['category']['slug']
        parent_slug = category['category']['parent_slug'] or None
        category_slug = 'shopping-services' if category_slug == 'retail-services' else category_slug
        parent_slug = 'shopping-services' if parent_slug == 'retail-services' else parent_slug
        categories_dict[category_slug] = parent_slug
    category_count = len(categories_dict.keys())
    parent_count = len(filter(None, set(categories_dict.values())))
    try:
        print 'Category tree established with {} categories and {} parents.\n'.format(category_count, parent_count)
    except:
        pass
    return categories_dict

def get_or_create_merchant(merchant_data_dict):
    ref_id = merchant_data_dict['id']
    merchant_model, created = Merchant.all_objects.get_or_create(ref_id=ref_id, ref_id_source='sqoot',
                                                             name=merchant_data_dict['name'])

    if created:
        print "Created merchant %s" % merchant_data_dict['name']

    merchant_model.link                 = merchant_data_dict['url']
    merchant_model.directlink           = merchant_data_dict['url']
    merchant_model.save()
    return merchant_model

def get_or_create_category(each_deal_data_dict, categories_dict):
    '''Manual renaming of "Retail & Services" to "Shopping & Services"'''
    category_slug = each_deal_data_dict['category_slug']
    category_name = each_deal_data_dict['category_name']
    if category_slug == 'retail-services':
        category_slug = 'shopping-services'
        category_name = 'Shopping & Services'
    if not category_slug:
        # In case where Sqoot doesn't show any category for a given deal
        return None
    parent_slug = categories_dict[category_slug]
    try:
        category_model = Category.objects.get(code=category_slug, ref_id_source='sqoot')
    except Category.DoesNotExist:
        category_model                    = Category()
        category_model.ref_id_source      = 'sqoot'
        category_model.code               = category_slug

    if parent_slug:
        try:
            parent_category               = Category.objects.get(code=parent_slug, ref_id_source='sqoot')
            category_model.parent         = parent_category
        except Category.DoesNotExist:
            parent_category = Category(ref_id_source='sqoot', code=parent_slug)
            parent_category.save()
            category_model.parent         = parent_category
    else:
        category_model.parent             = None

    # In case it was already created as another category's parent (hence save outside try-except)
    category_model.name = category_name
    category_model.save()
    return category_model

def get_or_create_dealtype():
    '''Treat all deals from sqoot as 'local' deals.'''

    dealtype_model, created = DealType.objects.get_or_create(code='local')
    if created:
        print "Created deal type 'local'"
        dealtype_model.name = 'Local'
        dealtype_model.save()
    return dealtype_model

def get_or_create_country():
    '''
    All deals from sqoot are US deals for now
    (They say they are going to add international deals at some point)
    '''
    country_model, created = Country.objects.get_or_create(code='usa')
    if created:
        print 'Created country entry for USA'
        country_model.name = 'usa'
        country_model.save()
    return country_model

def get_or_create_couponnetwork(each_deal_data_dict):
    provider_slug = each_deal_data_dict['provider_slug']
    couponnetwork_model, created = CouponNetwork.objects.get_or_create(code=provider_slug)
    if created:
        print 'Created coupon network %s' % each_deal_data_dict['provider_name']
        couponnetwork_model.name = each_deal_data_dict['provider_name']
        couponnetwork_model.save()
    return couponnetwork_model

def get_or_create_merchantlocation(merchant_data_dict, merchant_model, is_online_bool):
    '''
    If it's an online deal or lat/long data aren't available, this function does nothing.
    '''

    longitude = merchant_data_dict['longitude']
    latitude = merchant_data_dict['latitude']
    point_wkt = 'POINT({} {})'.format(longitude, latitude)

    if is_online_bool == True or longitude == None or latitude == None:
        return
    else:
        merchantlocation_model, created = MerchantLocation.objects.get_or_create(geometry=point_wkt, merchant=merchant_model)
        if created:
            print 'Created location %s, %s for merchant %s' % (merchant_data_dict['locality'], merchant_data_dict['address'],
                                                               merchant_model.name)
            merchantlocation_model.address      = merchant_data_dict['address']
            merchantlocation_model.locality     = merchant_data_dict['locality']
            merchantlocation_model.region       = merchant_data_dict['region']
            merchantlocation_model.postal_code  = merchant_data_dict['postal_code']
            merchantlocation_model.country      = merchant_data_dict['country']
            merchantlocation_model.save()
    return merchantlocation_model

def get_or_create_coupon(each_deal_data_dict, merchant_model, category_model, dealtype_model,
                         country_model, couponnetwork_model, merchantlocation_model):
    ref_id = each_deal_data_dict['id']
    coupon_model, created = Coupon.all_objects.get_or_create(ref_id=ref_id, ref_id_source='sqoot')
    if created:
        print 'Created coupon %s' % each_deal_data_dict['title']
        coupon_model.online              = each_deal_data_dict['online']
        coupon_model.merchant            = merchant_model
        coupon_model.merchant_location   = merchantlocation_model
        coupon_model.description         = strip_tags(each_deal_data_dict['description']) if each_deal_data_dict['description'] else None
        coupon_model.restrictions        = strip_tags(each_deal_data_dict['fine_print']) if each_deal_data_dict['fine_print'] else None
        coupon_model.start               = get_date(each_deal_data_dict['created_at'])
        coupon_model.end                 = get_date(each_deal_data_dict['expires_at'])
        coupon_model.link                = each_deal_data_dict['url']
        coupon_model.directlink          = each_deal_data_dict['untracked_url']
        coupon_model.skimlinks           = each_deal_data_dict['url']
        coupon_model.status              = 'unconfirmed'
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
    return coupon_model

def check_and_mark_duplicate(coupon_model):
    other_coupons_from_this_merchant = Coupon.all_objects.filter(merchant__ref_id=coupon_model.merchant.ref_id).exclude(ref_id=coupon_model.ref_id)
    if other_coupons_from_this_merchant.filter(is_duplicate=False).count() == 0:
        # This is the case where coupon_model already exists in db as a 'representative' i.e. is_duplicate=False
        return

    for c in other_coupons_from_this_merchant:
        info_match_count = 0
        info_match_count += 1 if coupon_model.description == c.description else 0
        info_match_count += 1 if coupon_model.embedly_title == c.embedly_title else 0
        info_match_count += 1 if coupon_model.embedly_description == c.embedly_description else 0
        info_match_count += 1 if coupon_model.price == c.price else 0
        info_match_count += 1 if coupon_model.listprice == c.listprice else 0
        if info_match_count == 5:
            coupon_model.is_duplicate = True
            Coupon.all_objects.filter(related_deal=coupon_model).update(related_deal=None)
            coupon_model.save()
            break

        if c.is_duplicate == True:
            continue

        if coupon_model.percent > c.percent:
            c.is_duplicate = True
            coupons_folded_under_c = Coupon.all_objects.filter(related_deal=c)
            for coupon_obj in coupons_folded_under_c:
                coupon_obj.related_deal = coupon_model
                coupon_obj.save()
            Coupon.all_objects.filter(related_deal=c).update(related_deal=None)
            c.related_deal = coupon_model
            c.save()
        else:
            coupon_model.is_duplicate = True
            coupon_model.related_deal = c
            coupon_model.save()

def check_if_deal_gone(coupon_obj):
    '''
    Note on coupon status:
    'unconfirmed' (default)
    'confirmed-inactive'
    'considered-active'
    '''
    url = coupon_obj.directlink
    provider_slug = coupon_obj.coupon_network.code

    if provider_slug == 'yelp':
        is_bad_link, page = check_if_bad_link(url)
        if is_bad_link:
            mark_deal_inactive(coupon_obj)
            return

        soup = BeautifulSoup(page.content)
        done_deal = soup.find("a", { "class" : "done-deal" })
        sold_out = soup.find("a", { "class" : "sold-out" })
        if done_deal or sold_out:
            mark_deal_inactive(coupon_obj)
            return

    if provider_slug == 'restaurant-com':
        is_bad_link, page = check_if_bad_link(url)
        if is_bad_link:
            mark_deal_inactive(coupon_obj)
            return

        if "ErrPgNotAvail" in page.url:
            mark_deal_inactive(coupon_obj)
            return

    coupon_obj.status = 'considered-active'
    coupon_obj.save()

def mark_deal_inactive(coupon_obj):
    coupon_obj.status = 'confirmed-inactive'
    coupon_obj.save()

def check_if_bad_link(url):
    if not url:
        return True, None
    page = requests.get(url)
    if page.status_code != 200:
        return True, None
    return False, page


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
