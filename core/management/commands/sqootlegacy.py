################################################################################################
#
# Below has not been maintained up to date yet. To be revisited (13 Feb 2014)
#
################################################################################################

from optparse import make_option
import os
import json
import math
import time

import requests
from geopy import geocoders

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q

from core.models import Category, Coupon
from readonly.scrub_list import SCRUB_LIST
from tests.for_api.sample_data_feed import top_50_us_cities_dict
from core.util import print_stack_trace
from core.util.sqootutils import (reorganize_categories_list, establish_categories_dict,
                                  get_or_create_category, describe_section, show_time, crosscheck_by_field,)

SQOOT_API_URL = "http://api.sqoot.com/v2/"
ITEMS_PER_PAGE = 100

class Command(BaseCommand):
    '''
    Summary Sqootload instructions:
    * --fullcycle (daily full cycle):
        * A wraper function meant to be run as a daily maintance task.
        * Runs refresh_sqoot_data(), validate_sqoot_data(), clean_out_sqoot_data(), dedup_sqoot_data_hard() all together.
        * To run:
            * Takes 'firsttime' argument if deployed & run for the first time.
              (e.g. ./manage.py sqootload firsttime --fullcycle)
            * Following the first time, 'firsttime' argument can be dropped (e.g. ./manage.py sqootload --fullcycle),
              provided that the first run was succesfully completed with a log.
        * Reads and logs summary stats from/into 'sqootload_running_log.txt' under 'logonly' folder when finished.
    * --validate (daily short & interim cycle):
        * Fetch a deal page and validate deal information and availabilty.
        * Meant to be run daily between the --fullcycle runs.
        * Takes 'pulseonly' argument for running on a standalone basis, separately from --fullcycle;
          When 'pulseonly' argument given, only the availabilty of the deal will be checked.
        * To run:
            * (e.g. ./manage.py sqootload pulseonly --validate)
    '''
    option_list = BaseCommand.option_list + (
        make_option('--savedown',
            action='store_true',
            dest='savedown',
            default=False,
            help='savedown'),
        make_option('--analyze',
            action='store_true',
            dest='analyze',
            default=False,
            help='analyze'),
        make_option('--scrubprepare',
            action='store_true',
            dest='scrubprepare',
            default=False,
            help='scrubprepare'),
        make_option('--scrubexecute',
            action='store_true',
            dest='scrubexecute',
            default=False,
            help='scrubexecute'),
        )

    def handle(self, *args, **options):
        if options['savedown']:
            try:
                savedown_sqoot_data()
            except:
                print_stack_trace()
        if options['analyze']:
            try:
                analyze_sqoot_deals()
            except:
                print_stack_trace()
        if options['scrubprepare']:
            try:
                prepare_list_of_deals_to_scrub()
            except:
                print_stack_trace()
        if options['scrubexecute']:
            try:
                read_scrub_list_and_update(args)
            except:
                print_stack_trace()


def savedown_sqoot_data():
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
    }
    print "\nSQOOT DATA LOAD STARTING..", show_time()

    categories_array = requests.get(SQOOT_API_URL + 'categories', params=request_parameters, timeout=5).json()['categories']
    categories_dict = establish_categories_dict(categories_array)
    reorganized_categories_array = reorganize_categories_list(categories_array)
    for category_dict in reorganized_categories_array:
        get_or_create_category(category_dict, categories_dict)

    # loading coupons and merchants
    describe_section("CHECKING THE LATEST DEAL DATA FROM SQOOT..", show_time())
    request_parameters['per_page'] = ITEMS_PER_PAGE
    active_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()['query']['total']
    page_count = int(math.ceil(active_deal_count / float(request_parameters['per_page'])))

    print '%s deals detected, estimating %s pages to iterate' % (active_deal_count, page_count), show_time()

    describe_section("STARTING TO DOWNLOAD SQOOT DEALS..", show_time())

    sqoot_file = open("sqoot_output.json", "w")
    sqoot_file.write("[")
    for p in range(page_count):
        request_parameters['page'] = p + 1
        print '## Fetching page %s...' % (p + 1), show_time()
        response_in_json = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()
        sqoot_file.write(json.dumps(response_in_json))
        sqoot_file.write(",")
    sqoot_file.write("]")
    sqoot_file.flush()
    sqoot_file.close()

def analyze_sqoot_deals():
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
    }

    # describe_section("Retrieving the latest categories..\n")
    # categories_array = requests.get(SQOOT_API_URL + 'categories', params=request_parameters).json()['categories']
    # category_slugs = [c['category']['slug'] for c in categories_array]

    describe_section("Retrieving the latest providers..\n")
    providers_array = requests.get(SQOOT_API_URL + 'providers', params=request_parameters, timeout=5).json()['providers']
    provider_slugs = [c['provider']['slug'] for c in providers_array]

    describe_section("Importing the latest 50 US cities..\n")
    target_cities = top_50_us_cities_dict

    describe_section("Checking total sqoot deals available..\n")
    total_deals_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()['query']['total']

    TARGET_RADIUS = 50 # miles
    request_parameters['radius'] = TARGET_RADIUS
    describe_section("Checking sqoot deals currently available in {} mi radius of the following cities..\n".format(TARGET_RADIUS))
    for city in target_cities:
        request_parameters['location'] = target_cities[city]
        per_city_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()['query']['total']
        print city, ': ', per_city_deal_count
    print 'total sqoot deal count: ', total_deals_count

    del request_parameters['location']

    describe_section("Preparing to check deal availablity from the following providers..\n")
    for p in provider_slugs:
        print p

    for p in provider_slugs:
        request_parameters['provider_slugs'] = p
        per_p_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()['query']['total']
        if per_p_deal_count < 100:
            print "total deals available from {} too small: {}".format(p, per_p_deal_count)
            print "Skipping.."
            continue
        else:
            describe_section("Checking deals from {} for each city..\n".format(p))

        for city in target_cities:
            request_parameters['location'] = target_cities[city]
            per_city_and_p_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()['query']['total']
            print city, ': ', per_city_and_p_deal_count
        print 'total {} deal count:  {}'.format(p, per_p_deal_count)
        del request_parameters['location']

def prepare_list_of_deals_to_scrub():
    start_time = time.time()
    deals_to_scrub = Coupon.all_objects.filter(pk__in=SCRUB_LIST).order_by('merchant__name')

    probably_dup_deals_list = [] # List of coupon pks that look like a duplicate.
    probably_dup_deals_list = crosscheck_by_field(deals_to_scrub, probably_dup_deals_list, 'coupon_directlink')
    probably_dup_deals_list = crosscheck_by_field(deals_to_scrub, probably_dup_deals_list, 'merchant_name')
    probably_dup_deals_list = list(set(probably_dup_deals_list))

    print "merchant_pk^merchant_ref_id^merchant_name^address^locality^region^postal_code^coupon_pk^coupon_ref_id^coupon_title^coupon_short_title^parent_category^child_category^deal_price^deal_value^provider^link^is_duplicate?"

    for d in deals_to_scrub:
        categories      = d.categories.all()
        parent_category = [cat for cat in categories if cat.parent == None]
        parent_category = parent_category[0].name if parent_category else None
        child_category  = [cat for cat in categories if cat.parent != None]
        child_category  = child_category[0].name if child_category else None

        address         = d.merchant_location.address if d.merchant_location.address else ""
        locality        = d.merchant_location.locality if d.merchant_location.locality else ""
        region          = d.merchant_location.region if d.merchant_location.region else ""
        postal_code     = d.merchant_location.postal_code if d.merchant_location.postal_code else ""

        if d.pk in probably_dup_deals_list:
            is_duplicate = 1
        else:
            is_duplicate = 0

        try:
            print "%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s^%s" %\
                  (d.merchant.pk, d.merchant.ref_id, d.merchant.name.lower(), address, locality, region, postal_code, d.pk, d.ref_id, d.embedly_title,\
                   d.embedly_description, parent_category, child_category, d.price, d.listprice, d.coupon_network.name, d.directlink, is_duplicate)
        except:
            print "!!!ERROR: merchant_pk == {}".format(d.merchant.pk)
            print_stack_trace()
            continue

    end_time = time.time()
    time_elapsed = end_time - start_time
    print time_elapsed

def read_scrub_list_and_update(args):
    try:
        filename = args[0]
    except:
        pass

    # Thomas' Bing Geocoder api key (free basic access)
    # dotus_geocoder  = geocoders.GeocoderDotUS() for consideration as a fallback
    bing_geocoder   = geocoders.Bing('AvxLEwiPhVJzf0S3Pozgg01NnUQQX0RR6g9K46VPLlZ8OfZkKS-76gaPyzoV6IHI')

    path = os.path.join(settings.BASE_DIR, 'readonly', filename)
    try:
        f = open(path)
    except IOError:
        print_stack_trace()

    rows = []
    for row in f:
        rows.append(row.replace("\r\n", "").split("\t"))

    for row in rows[1:]: # Skip the header
        try:
            coupon_pk           = int(row[1])
            is_duplicate        = True if row[3] == '1' else False
            is_inactive         = True if row[4] == '1' else False
            is_category_wrong   = True if row[5] == '1' else False
            is_location_wrong   = True if row[8] == '1' else False
            correction_needed   = is_duplicate or is_inactive or is_category_wrong or is_location_wrong

            if correction_needed:
                coupon_obj = Coupon.all_objects.get(pk=coupon_pk)
                if is_duplicate:
                    coupon_obj.is_duplicate = True
                    # print "Correction: ", coupon_pk, " is_duplicate=True" #DEBUG
                if is_inactive:
                    coupon_obj.status = 'confirmed-inactive'
                    # print "Correction: ", coupon_pk, " status=confirmed-inactive" #DEBUG
                if is_category_wrong:
                    coupon_obj.categories.clear()
                    try:
                        parent_category = Category.objects.get(ref_id_source='sqoot', name=row[6])
                        coupon_obj.categories.add(parent_category)
                        # print "Correction: ", coupon_pk, " Parent category -> ", parent_category.name #DEBUG
                    except:
                        pass

                    try:
                        child_category  = Category.objects.get(ref_id_source='sqoot', name=row[7])
                        coupon_obj.categories.add(child_category)
                        # print "Correction: ", coupon_pk, " Child category -> ", child_category.name #DEBUG
                    except:
                        pass
                if is_location_wrong:
                    location_obj = coupon_obj.merchant_location
                    address      = row[9] if row[9] != '' else ''
                    locality     = row[10] if row[10] != '' else ''
                    region       = row[11] if row[11] != '' else ''
                    postal_code  = row[12] if row[12] != '' else ''
                    spacer1      = ', ' if address != '' else ''
                    spacer2      = ' ' if locality != '' else ''
                    lookup_text  = address + spacer1 + locality + spacer2 + region

                    try:
                        place, (lat, lng) = bing_geocoder.geocode(lookup_text)
                        pnt = 'POINT({} {})'.format(lng, lat)
                        location_obj.geometry = pnt
                    except:
                        pass

                    location_obj.address     = address if address != '' else location_obj.address
                    location_obj.locality    = locality if locality != '' else location_obj.locality
                    location_obj.region      = region if region != '' else location_obj.region
                    location_obj.postal_code = postal_code if postal_code != '' else location_obj.postal_code
                    location_obj.save()
                    # print "Correction: ", coupon_pk, " Location fixed" #DEBUG
                coupon_obj.save()
        except:
            print_stack_trace()

    scrub_list_retrieved = [row[1] for row in rows[1:]] # list of original coupon pks imported from 'scrub_list.py'
    deals_to_scrub = Coupon.all_objects.filter(pk__in=scrub_list_retrieved)\
                                       .exclude(Q(status='confirmed-inactive') | Q(status='implied-inactive') | Q(is_duplicate=True))\
                                       .order_by('merchant__name')

    probably_dup_deals_list = [] # List of coupon pks that look like a duplicate.
    probably_dup_deals_list = crosscheck_by_field(deals_to_scrub, probably_dup_deals_list, 'coupon_directlink')
    probably_dup_deals_list = crosscheck_by_field(deals_to_scrub, probably_dup_deals_list, 'merchant_name')
    probably_dup_deals_list = list(set(probably_dup_deals_list))

    for pk in probably_dup_deals_list:
        try:
            coupon = Coupon.all_objects.get(pk=pk)
            coupon.is_duplicate = True
            coupon.save()
            # print "Correction: ", coupon_pk, " is_duplicate=True" #DEBUG
        except:
            print_stack_trace()

