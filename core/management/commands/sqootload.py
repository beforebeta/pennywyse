# -*- coding: utf-8 -*-
import os
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import math
import time
import re
import requests
from optparse import make_option
import csv

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.html import strip_tags
from django.db.models import Q, Max

from BeautifulSoup import BeautifulSoup
from fuzzywuzzy import fuzz
from geopy import geocoders
# from haystack.utils.geo import D
# from haystack.query import SearchQuerySet, SQ
import pytz

from core.models import DealType, Category, Coupon, Merchant, Country, CouponNetwork, MerchantLocation
from tests.for_api.sample_data_feed import top_50_us_cities_dict
from readonly.scrub_list import SCRUB_LIST
from core.util import print_stack_trace
import json

SQOOT_API_URL = "http://api.sqoot.com/v2/"
ITEMS_PER_PAGE = 100
SAVED_MERCHANT_ID_LIST = [int(m.ref_id) for m in Merchant.all_objects.filter(ref_id_source='sqoot', is_deleted=False).only('ref_id')]

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--fullcycle',
            action='store_true',
            dest='fullcycle',
            default=False,
            help='fullcycle'),
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
        '''
        --fullcycle:    A wrapper function for running full cycle of sqootload functions
        --directload:   For downloading and loading coupons into db directly from sqoot
        --indirecload:  For loading coupons from a file saved via --savedown option
        --savedown:     For downloading coupons from sqoot and saving them into a file
        --validate:     For validating deal;
                        * If no args are given, it will validate all local deals that have no expiry date
                        * If multiple args are given (as CityPicture.code), then it will only validate deals within 100mi
                          of the target city by comaring against sqoot
        --scrubprepare: For preparing to do a semi-manual check process by outputting into '^' seperatated file
        --scrubexecute: For reading a tab seperatated file after checking semi-manually for data corrections;
                        * Takes one argument that is a file name under 'readonly' folder
        '''

        if options['fullcycle']:
            try:
                run_thru_full_cycle(args)
            except:
                print_stack_trace()
        if options['directload']:
            firsttime = True if 'firsttime' in args else False
            try:
                refresh_sqoot_data(firsttime=firsttime)
            except:
                print_stack_trace()
        if options['indirectload']:
            firsttime = True if 'firsttime' in args else False
            try:
                refresh_sqoot_data(indirectload=True, firsttime=firsttime)
            except:
                print_stack_trace()
        if options['savedown']:
            try:
                savedown_sqoot_data()
            except:
                print_stack_trace()
        if options['validate']:
            pulseonly = True if 'pulseonly' in args else False

            p = re.compile('selfstop')
            selfstop_given = filter(p.match, args)
            if selfstop_given:
                selfstop_string = selfstop_given[0]
                _, target_hour = selfstop_string.split('@') # target hour in 24 hours (00 - 23)
                ct = datetime.now() # ct -> current time; now() -> local time
                day_adj = 1 if ct.hour >= int(target_hour) else 0
                buffer_adj = timedelta(minutes=5)
                stoptime = datetime(ct.year, ct.month, ct.day + day_adj, int(target_hour)) - buffer_adj
            else:
                stoptime = None

            try:
                validate_sqoot_data(pulseonly=pulseonly, stoptime=stoptime)
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

def run_thru_full_cycle(args):
    firsttime = True if 'firsttime' in args else False

    path = os.path.join(settings.BASE_DIR, 'logonly', 'sqootload_running_log.txt')
    try:
        f = open(path, 'r')
    except IOError:
        print_stack_trace()

    all_rows = f.readlines()
    if len(all_rows) == 1:
        last_row = None
    else:
        last_row = all_rows[-1]
        latest_stats = last_row.replace('\r\n', '').split(',')
    f.close()

    last_run_start_time = parse(latest_stats[0]) if last_row else None
    last_inventory_count = int(latest_stats[7])  if last_row else 0
    beg_inventory_count = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                    is_duplicate=False, online=False,
                                                    status='considered-active',
                                                    end__gt=datetime.now(pytz.utc)).count()
    implied_attrition = last_inventory_count - beg_inventory_count if last_inventory_count else 0
    fullcycle_starttime = datetime.now(pytz.utc)
    refresh_start_time, refresh_end_time, sqoot_raw_active, num_of_soft_dedups = refresh_sqoot_data(last_run_start_time, firsttime=firsttime)
    _, num_of_implied_inactive, cleanout_endtime = clean_out_sqoot_data(refresh_start_time)
    num_of_confirmed_inactive, validate_endtime = validate_sqoot_data(refresh_start_time)
    num_of_hard_dedups, hard_dedup_endtime = dedup_sqoot_data_hard(refresh_start_time, firsttime=firsttime)
    clean_out_sqoot_data(refresh_start_time)
    end_inventory_count = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                            is_duplicate=False, online=False,
                                                            status='considered-active').count()
    fullcycle_endtime = datetime.now(pytz.utc)
    describe_section("ALL DONE AND LOGGING THINGS..\n")

    num_of_total_inactives = num_of_implied_inactive + num_of_confirmed_inactive
    num_of_total_dedups = num_of_soft_dedups + num_of_hard_dedups
    implied_net_adds = end_inventory_count - (beg_inventory_count - num_of_total_inactives - num_of_total_dedups)

    refresh_took = refresh_end_time - refresh_start_time
    validate_took = validate_endtime - cleanout_endtime
    hard_dedup_took = hard_dedup_endtime - validate_endtime

    with open(path, 'a') as csvfile:
        log_writer = csv.writer(csvfile)
        log_writer.writerow([fullcycle_starttime, last_inventory_count, beg_inventory_count,
                             implied_attrition, num_of_total_inactives, num_of_total_dedups,
                             implied_net_adds, end_inventory_count, fullcycle_endtime, refresh_took.seconds/60,
                             validate_took.seconds/60, hard_dedup_took.seconds/60])
    csvfile.close()

def refresh_sqoot_data(last_run_start_time, indirectload=False, firsttime=False):
    refresh_start_time = datetime.now(pytz.utc) # Use UTC time to compare & update coupon's 'last_modified' field
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
    }
    print "\nSQOOT DATA LOAD STARTING..\n"

    # loading categories
    describe_section("ESTABLISHING CATEGORY DICTIONARY..\n")
    categories_array = requests.get(SQOOT_API_URL + 'categories', params=request_parameters).json()['categories']
    categories_dict = establish_categories_dict(categories_array) # Returns a dict with child: parent categories
    reorganized_categories_array = reorganize_categories_list(categories_array) # list of dict with 'category_name', and 'category_slug'
    for category_dict in reorganized_categories_array:
        get_or_create_category(category_dict, categories_dict)

    # loading coupons and merchants
    describe_section("CHECKING THE LATEST DEAL DATA FROM SQOOT..\n")
    request_parameters['per_page'] = ITEMS_PER_PAGE
    sqoot_active_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['query']['total']
    page_count = int(math.ceil(sqoot_active_deal_count / float(request_parameters['per_page'])))
    print '%s deals detected, estimating %s pages to iterate\n' % (sqoot_active_deal_count, page_count)

    describe_section("STARTING TO DOWNLOAD SQOOT DEALS..\n")
    # Since there's only one country & dealtype for all sqoot deals - no need to check it for each coupon
    country_model       = get_or_create_country()
    dealtype_model      = get_or_create_dealtype()

    # two_days_ago_datetime = datetime.now() - timedelta(days=2) # 1 day buffer based on daily run assumption, hence 2 days
    sqoot_output_deals = None
    if indirectload:
        sqoot_output_deals = json.loads(open("sqoot_output.json","r").read())

    num_of_soft_dedups = 0
    for p in range(page_count):
    # for p in range(55): # DEBUG!!!
    #     if p < 40: # DEBUG!!!
    #         continue
        request_parameters['page'] = p + 1
        print '## Fetching page %s...\n' % (p + 1)

        if indirectload:
            response_in_json = sqoot_output_deals[p]
        else:
            response_in_json = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()

        active_coupon_ids = [] # List of sqoot coupon ids to hold all active deal ids per page, as set 'page' request_parameters.
        deals_data = response_in_json['deals']
        for deal_data in deals_data:
            sqoot_coupon_id = int(deal_data['deal']['id'])
            active_coupon_ids.append(sqoot_coupon_id)

            deal_last_updated = parse(deal_data['deal']['updated_at']+'+0000')
            if (not firsttime) and (deal_last_updated < last_run_start_time):
                continue

            try:
                is_online_bool = deal_data['deal']['online']
                merchant_data_dict = deal_data['deal']['merchant']


                # Note: Only retrieve if already exists: 'couponnetwork_model', 'category_model', 'merchantlocation_model'
                # Note: Update with the latest data from sqoot even if exists: 'merchant_model', 'coupon_model'
                # 'shortcut=True' is given for get_or_create_category() since all categories were 'get_or_create'd above.
                couponnetwork_model      = get_or_create_couponnetwork(deal_data['deal'])
                category_model           = get_or_create_category(deal_data['deal'], categories_dict, shortcut=True)
                merchant_model           = get_or_create_merchant(merchant_data_dict)
                merchantlocation_model   = get_or_create_merchantlocation(merchant_data_dict, merchant_model, is_online_bool)
                coupon_model             = get_or_create_coupon(deal_data['deal'], merchant_model, category_model, dealtype_model,
                                                                country_model, couponnetwork_model, merchantlocation_model)

                coupon_ref_id = int(coupon_model.merchant.ref_id)
                if coupon_ref_id not in SAVED_MERCHANT_ID_LIST:
                    SAVED_MERCHANT_ID_LIST.append(coupon_ref_id)
                else:
                    dedup_scoot_data_soft(coupon_model)
                    num_of_soft_dedups += 1

                print '-' * 60
            except:
                print_stack_trace()
        Coupon.all_objects.filter(ref_id_source='sqoot', ref_id__in=active_coupon_ids).update(last_modified=datetime.now(pytz.utc))
    refresh_end_time = datetime.now(pytz.utc)
    return refresh_start_time, refresh_end_time, sqoot_active_deal_count, num_of_soft_dedups

def clean_out_sqoot_data(refresh_start_time):
    '''
    Summary: Internal garbage collection cycle that finds and soft-delete all
             irrelevant and stale local coupons and merchants.
    Intent:
    * First find all true duplicate deals and soft-delete them
      (i.e. is_duplicate=True, related_deal__isnull=True)
    * Second, find all folded deals (i.e. is_duplicate=True, related_deal__isnull=True)
      that are stale (either expired or inactive, both implied and confirmed), and soft-delete them
    * Third, find all unique deals that are stale, check for folded deals (if so, reassign)
      and soft-delete them.
    * Fourth, find all inactive merchants (no active deals), and soft-delete them.
    '''
    describe_section("clean_out_sqoot_data IS BEGINNING..\n")
    affected_merchant_list = [] # collect a list of merchant pks whose coupons are being soft-deleted
    num_of_soft_deleted = 0

    # First
    true_duplicate_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                     is_duplicate=True, related_deal__isnull=True)
    num_of_soft_deleted += true_duplicate_deals.update(is_deleted=True)
    affected_merchant_list += [c.merchant.pk for c in true_duplicate_deals]

    # Second
    folded_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                             is_duplicate=True, related_deal__isnull=False)
    num_of_soft_deleted += folded_deals.filter(last_modified__lt=refresh_start_time).update(status='implied-inactive', is_deleted=True)
    num_of_soft_deleted += folded_deals.filter(status='confirmed-inactive').update(is_deleted=True)
    num_of_soft_deleted += folded_deals.filter(end__lt=datetime.now(pytz.utc)).update(is_deleted=True)
    affected_merchant_list += [c.merchant.pk for c in folded_deals]

    # Third (Second -> Third; the order matters)
    non_dup_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False, is_duplicate=False)\
                                      .filter(Q(last_modified__lt=refresh_start_time)\
                                            | Q(status='confirmed-inactive')\
                                            | Q(end__lt=datetime.now(pytz.utc)))
    deals_with_folded_deals = [c.pk for c in non_dup_deals if Coupon.all_objects.filter(related_deal=c).count() != 0]
    for i in deals_with_folded_deals:
        reassign_representative_deal(Coupon.all_objects.get(pk=i))
    num_of_implied_inactive = non_dup_deals.filter(last_modified__lt=refresh_start_time).update(status='implied-inactive', is_deleted=True)
    num_of_soft_deleted += non_dup_deals.filter(status='confirmed-inactive').update(is_deleted=True)
    num_of_soft_deleted += non_dup_deals.filter(end__lt=datetime.now(pytz.utc)).update(is_deleted=True)
    affected_merchant_list += [c.merchant.pk for c in non_dup_deals]

    # Fourth
    affected_merchant_list = list(set(affected_merchant_list))
    inactive_merchant_list = []
    for mpk in affected_merchant_list:
        miq = Merchant.all_objects.get(pk=mpk) # merchant-in-question (miq)
        num_of_active_coupons_from_miq = Coupon.all_objects.filter(ref_id_source='sqoot',\
                                                                   merchant=miq, is_deleted=False).count()
        if num_of_active_coupons_from_miq:
            continue
        else:
            inactive_merchant_list.append(miq.pk)
    Merchant.all_objects.filter(pk__in=inactive_merchant_list).update(is_deleted=True)

    num_of_soft_deleted += num_of_implied_inactive
    cleanout_endtime = datetime.now(pytz.utc)
    return num_of_soft_deleted, num_of_implied_inactive, cleanout_endtime

def validate_sqoot_data(refresh_start_time=None, pulseonly=False, stoptime=None):
    describe_section("validate_sqoot_data IS BEGINNING..\n")
    '''
    Summary: Fetch a deal page and validate deal information and availabilty.

    Intent:
    * Check for two things (i) deal information (price and location) and (ii) deal availability.
    * If (i) isn't correct, correct them. If (ii) is not available, mark them 'confirmed-inactive'.
    '''
    all_active_deals_on_display = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                            is_duplicate=False, online=False)\
                                                    .filter(Q(status='unconfirmed') | Q(status='considered-active'))
    considered_active_list = [] # coupon pk's
    confirmed_inactive_list = [] # coupon pk's
    blah_counter = 0 #DEBUG!!!
    for c in all_active_deals_on_display:
        try:
            if stoptime and (datetime.now() >= stoptime):
                break

            sqoot_url = c.directlink
            is_bad_link, response = fetch_page(sqoot_url)
            if is_bad_link:
                confirmed_inactive_list.append(c.pk)
                continue

            is_deal_dead = check_if_deal_dead(c, response, sqoot_url)
            if is_deal_dead:
                confirmed_inactive_list.append(c.pk)
            else:
                considered_active_list.append(c.pk)

            if pulseonly and refresh_start_time and (refresh_start_time > c.date_added):
                # Data check only the newly added deals.
                continue
            else:
                confirm_or_correct_deal_data(c, response)
            blah_counter += 1 #DEBUG!!!
            print '.......validated', blah_counter # DEBUG!!!
        except:
            print_stack_trace()
    Coupon.all_objects.filter(pk__in=considered_active_list).update(status='considered-active')
    num_of_confirmed_inactive = Coupon.all_objects.filter(pk__in=confirmed_inactive_list).update(status='confirmed-inactive')
    validate_endtime = datetime.now(pytz.utc)
    return num_of_confirmed_inactive, validate_endtime

def dedup_sqoot_data_hard(refresh_start_time, firsttime=False):
    describe_section("dedup_sqoot_data_hard IS BEGINNING..\n")
    # Grab all active deals on display to users for deduping.
    deals_to_dedup = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                               is_duplicate=False, online=False, status='considered-active')
    if not firsttime:
        # If not first time, further filter down to only the newly added unique deals for deduping.
        deals_to_dedup = deals_to_dedup.filter(date_added__gt=refresh_start_time)

    duplicate_deals_list = [] # List of duplicate coupon pks .
    duplicate_deals_list = crosscheck_by_field(deals_to_dedup, duplicate_deals_list, 'coupon_directlink')
    duplicate_deals_list = crosscheck_by_field(deals_to_dedup, duplicate_deals_list, 'merchant_name')
    duplicate_deals_list = list(set(duplicate_deals_list))

    num_of_hard_dedups = Coupon.all_objects.filter(pk__in=duplicate_deals_list).update(is_duplicate=True)
    hard_dedup_endtime = datetime.now(pytz.utc)
    return num_of_hard_dedups, hard_dedup_endtime


#############################################################################################################
#
# Helper Methods - Passive Commands
#
#############################################################################################################

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


#############################################################################################################
#
# Helper Methods - Data Gathering
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
    else:
        print "UPDATING merchant %s" % merchant_data_dict['name']
    merchant_model.link         = merchant_data_dict['url']
    merchant_model.directlink   = merchant_data_dict['url']
    merchant_model.is_deleted   = False
    merchant_model.save()
    return merchant_model

def get_or_create_category(each_deal_data_dict, categories_dict, shortcut=False):
    '''
    * Manual renaming of "Retail & Services" to "Shopping & Services"
    * 'shortcut' option is for simply retreiving the category object.
    '''
    category_slug = each_deal_data_dict['category_slug']
    category_name = each_deal_data_dict['category_name']
    if category_slug == 'retail-services':
        category_slug = 'shopping-services'
        category_name = 'Shopping & Services'
    if not category_slug:
        return None # In case where Sqoot doesn't show any category for a given deal

    try:
        category_model = Category.objects.get(code=category_slug, ref_id_source='sqoot')
    except Category.DoesNotExist:
        category_model = Category(ref_id_source='sqoot', code=category_slug, name=category_name)
        category_model.save()

    if shortcut:
        return category_model

    parent_slug = categories_dict[category_slug]
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
        return None

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
    else:
        print 'UPDATING coupon %s' % each_deal_data_dict['title']
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
    coupon_model.is_deleted          = False
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

#############################################################################################################
#
# Helper Methods - Data Intelligence
#
#############################################################################################################

def dedup_scoot_data_soft(coupon_model):
    '''
    Check all deals under the same merchant, mark duplicate deals, and fold them under the best deal
    '''
    if coupon_model.online == True:
        return

    other_coupons_from_this_merchant = Coupon.all_objects.filter(merchant__ref_id=coupon_model.merchant.ref_id, is_deleted=False)\
                                                         .exclude(ref_id=coupon_model.ref_id)
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

def reassign_representative_deal(coupon_model):
    '''
    Summary: Scan folded deals and reassign a repr. deal out of them before removing the current rep.

    Intent: Look for an alternative rep. deal based on the best discount
    Note: This function assumes that coupon_model has folded deals (>0) under it.
    '''
    merchant_sqoot_id = coupon_model.merchant.ref_id
    candidates = Coupon.all_objects.filter(merchant__ref_id=merchant_sqoot_id, is_deleted=False)\
                                   .exclude(ref_id=coupon_model.ref_id)
    max_disc_percent = candidates.aggregate(Max('percent'))['percent__max']
    new_rep_deal = candidates.filter(percent=max_disc_percent)[0]
    new_rep_deal.is_duplicate = False
    new_rep_deal.related_deal = None
    new_rep_deal.save()
    candidates.exclude(pk=new_rep_deal.pk).update(related_deal=new_rep_deal)

def fetch_page(sqoot_url, tries=1):
    '''
    Summary: Check if url is valid and return a boolean with a response.
    '''
    try:
        if not sqoot_url:
            return True, None
        response = requests.get(sqoot_url)
        if response.status_code != 200:
            return True, None
        return False, response
    except Exception, e:
        print_stack_trace()
        print "^---- Offending URL: ", sqoot_url
        if tries < 3:
            print "Retrying in 5 seconds, maybe the server just needs a break"
            time.sleep(5)
            return fetch_page(sqoot_url, tries+1)
        else:
            raise e #reraise exception

def check_if_deal_dead(coupon_obj, response, sqoot_url):
    '''
    Summary: Check if deal is unavilable and return a boolean.

    Note on coupon status:
    'unconfirmed' (default)
    'confirmed-inactive'
    'considered-active'
    'implied-inactive' (Not used in this function; Refer to clean_out_sqoot_data() for this status)
    '''
    provider_slug = coupon_obj.coupon_network.code
    soup = BeautifulSoup(response.content)

    if provider_slug == 'livingsocial':
        deal_status = soup.find("span", { "class" : "btn btn-large disabled" })
        dead_deal_statuses = ['deal over', 'sold out!']
        if deal_status and (deal_status.text in dead_deal_statuses):
            return True

    if provider_slug == 'yelp':
        done_deal = soup.find("a", { "class" : "done-deal" })
        sold_out = soup.find("a", { "class" : "sold-out" })
        if done_deal or sold_out:
            return True

    if provider_slug == 'restaurant-com':
        if "ErrPgNotAvail" in response.url:
            return True

    if provider_slug == 'amazon-local':
        deal_status = soup.find("div", { "class" : "deal_buyability_status" })
        dead_deal_statuses = ['Deal Over', 'Sold Out']
        if deal_status and (deal_status.text in dead_deal_statuses):
            return True

    if provider_slug == 'goldstar':
        buy_button = soup.find("a", { "class" : "event-info-button button-flat" })
        if not buy_button:
            return True
        show_list = soup.find("ul", { "class" : "show_list" })
        options_count = len(show_list.findAll('li'))
        unavailable_count = len(show_list.findAll('a', { 'class' : ' unavailable' }))
        if unavailable_count >= options_count:
            return True

    if provider_slug == 'scorebig':
        soldout_head = soup.find("div", { "class" : "event-soldout-head" })
        if soldout_head:
            return True

    if provider_slug == 'groupon':
        expired_button = soup.find("button", { "class" : "btn-buy-big state-expired" })
        soldout_button = soup.find("button", { "class" : "btn-buy-big state-sold-out" })
        if expired_button or soldout_button:
            return True

    if provider_slug == 'crowdsavings':
        sold_out = soup.find("h2", { "class" : "sold right" })
        if sold_out:
            return True

    if provider_slug == 'dealchicken':
        time_ribbon = soup.find("p", { "id" : "timeRibbon" })
        soldout = soup.find("p", { "class" : "soldout" })
        if soldout or (time_ribbon and time_ribbon.text == "Sorry, this deal is over!"):
            return True

    if provider_slug == 'doubletake-deals':
        deal_region = sqoot_url.replace('http://www.doubletakedeals.com/deals/', '').split('/')[0]
        res_url_breakdown = response.url.replace('https://www.doubletakeoffers.com/', '').split('?')
        deal_disappeared = True if deal_region in res_url_breakdown else False

        no_offers = soup.find("div", { "class" : "noOffers" })
        soldout_one = soup.findAll('div', id=re.compile('SoldOutRemaining$'))
        soldout_two = soup.find("div", { "class" : "bowSoldout" })
        if deal_disappeared or no_offers or soldout_one or soldout_two:
            return True

    if provider_slug == 'travelzoo':
        soldout = soup.find("div", { "class" : "soldoutBox" })
        if soldout:
            return True

    return False

def confirm_or_correct_deal_data(coupon_model, response):
    pass

def crosscheck_by_field(deals_to_dedup, duplicate_deals_list, field_name):
    if field_name == 'coupon_directlink':
        field_list = list(set([d.directlink for d in deals_to_dedup]))
    elif field_name == 'merchant_name':
        field_list = list(set([d.merchant.name for d in deals_to_dedup]))
    else:
        return duplicate_deals_list

    for x in field_list:
        try:
            same_looking_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_duplicate=False,
                                                           is_deleted=False, online=False)\
                                                   .exclude(end__lt=datetime.now(pytz.utc))
            if field_name == 'coupon_directlink':
                same_looking_deals = same_looking_deals.filter(directlink=x)
            elif field_name == 'merchant_name':
                same_looking_deals = same_looking_deals.filter(merchant__name__contains=x)

            if same_looking_deals.count() <= 1:
                continue

            while True:
                current_count = same_looking_deals.count()
                if current_count == 1:
                    break
                else:
                    for c in same_looking_deals[1:current_count]:
                        if c.pk in duplicate_deals_list:
                            continue

                        does_it_look_duplicate, which_deal = compare_location_between(same_looking_deals[0], c)
                        if not does_it_look_duplicate:
                            continue

                        if which_deal == same_looking_deals[0]:
                            duplicate_deals_list.append(which_deal.pk)
                            break
                        else:
                            duplicate_deals_list.append(which_deal.pk)
                    same_looking_deals = same_looking_deals.exclude(pk=same_looking_deals[0].pk)
        except:
            print "!!!ERROR: field: {}".format(x)
            print_stack_trace()
    return duplicate_deals_list

def compare_location_between(deal_obj_one, deal_obj_two):
    location_one = deal_obj_one.merchant_location
    location_two = deal_obj_two.merchant_location

    if not location_one:
        return True, deal_obj_one # is_duplicate?, which_deal
    if not location_two:
        return True, deal_obj_two

    if not location_one.address:
        return True, deal_obj_one
    if not location_two.address:
        return True, deal_obj_two

    if location_one.postal_code == location_two.postal_code:
        address_one = cleanse_address_text(location_one.address)
        address_two = cleanse_address_text(location_two.address)
        match_ratio = fuzz.ratio(address_one.lower(), address_two.lower())

        if match_ratio >= 95:
            if not location_one.locality:
                return True, deal_obj_one
            if not location_two.locality:
                return True, deal_obj_two

            if deal_obj_one.percent >= deal_obj_two.percent:
                return True, deal_obj_two
            else:
                return True, deal_obj_one
        else:
            return False, None
    else:
        return False, None


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
        return datetime.strptime(clean_date_string, "%Y-%m-%d %H:%M")
    return None

def cleanse_address_text(address_string):
    address_crufts = ['Rd', 'Hwy', 'Dr', 'St', 'Ave', 'Blvd', 'Expy', 'Ln', 'E', 'S', 'W', 'N', 'Pkwy', 'Cir',\
                      'Road', 'Highway', 'Drive', 'Street', 'Avenue', 'Boulevard', 'Expressway', 'Lane', 'East', 'South', 'West', 'North', 'Parkway', 'Circle']
    address_broken_down = address_string.replace('.', '').split(' ')
    caught_crufts = [val for val in address_broken_down if val in address_crufts]
    for c in caught_crufts:
        address_broken_down.remove(c)
    clean_address = (' ').join(address_broken_down)
    return clean_address

