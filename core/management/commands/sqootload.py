# -*- coding: utf-8 -*-
import os
import math
import time
import csv
import json
from datetime import datetime
from dateutil.parser import parse
from multiprocessing import Pool
from itertools import repeat
from optparse import make_option

import pytz
import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q

from core.models import Coupon, Merchant
from core.util import print_stack_trace
from core.util.sqootutils import (reorganize_categories_list, establish_categories_dict, get_or_create_merchant,
                                  get_or_create_category, get_or_create_dealtype, get_or_create_country,
                                  get_or_create_couponnetwork, get_or_create_merchantlocation, get_or_create_coupon,
                                  fetch_page, confirm_or_correct_deal_data, check_if_deal_dead, reassign_representative_deal,
                                  describe_section, show_time, crosscheck_by_field,)

'''
Functions Flow Summary:
* run_thru_full_cycle()
    \- refresh_sqoot_data()
        \- dedup_scoot_data_soft()
    \- clean_out_sqoot_data()
    \- validate_sqoot_data()
        \- go_validate()
    \- dedup_sqoot_data_hard()
'''

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
        make_option('--validate',
            action='store_true',
            dest='validate',
            default=False,
            help='validate'),
        make_option('--deduphard',
            action='store_true',
            dest='deduphard',
            default=False,
            help='deduphard'),
    )

    def handle(self, *args, **options):
        if options['fullcycle']:
            try:
                run_thru_full_cycle(args)
            except:
                print_stack_trace()
        if options['directload']:
            firsttime = True if 'firsttime' in args else False
            last_run_start_time = None
            try:
                refresh_sqoot_data(last_run_start_time, firsttime=firsttime)
            except:
                print_stack_trace()
        if options['indirectload']:
            firsttime = True if 'firsttime' in args else False
            try:
                refresh_sqoot_data(indirectload=True, firsttime=firsttime)
            except:
                print_stack_trace()
        if options['validate']:
            pulseonly = True if 'pulseonly' in args else False
            stoptime = None # ignore for now
            try:
                validate_sqoot_data(pulseonly=pulseonly, stoptime=stoptime)
            except:
                print_stack_trace()
        if options['deduphard']:
            try:
                dedup_sqoot_data_hard()
            except:
                print_stack_trace()

def run_thru_full_cycle(args):
    '''
    Summary: A wrapper function to run daily refresh, validate, dedup and clean functions consecutively.

    Note: Takes 'firsttime' argument.
    '''
    firsttime = True if 'firsttime' in args else False
    path = os.path.join(settings.BASE_DIR, 'misc','logonly', 'sqootload_running_log.txt')
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
    last_refresh_time = parse(latest_stats[1]) if last_row else None

    describe_section("FULLCYCLE STARTING..", show_time())
    refresh_start_time, refresh_end_time = refresh_sqoot_data(last_refresh_time, firsttime=firsttime)
    with open(path, 'a') as csvfile:
        log_writer = csv.writer(csvfile)
        log_writer.writerow(['wip ', refresh_start_time,])
    csvfile.close()

    cleanout_endtime    = clean_out_sqoot_data(refresh_start_time)
    validate_endtime    = validate_sqoot_data(refresh_start_time)
    hard_dedup_endtime  = dedup_sqoot_data_hard(refresh_start_time, firsttime=firsttime)
    fullcycle_endtime   = datetime.now(pytz.utc)

    describe_section("ALL DONE AND LOGGING THINGS..", show_time())
    refresh_took        = refresh_end_time - refresh_start_time
    validate_took       = validate_endtime - cleanout_endtime
    hard_dedup_took     = hard_dedup_endtime - validate_endtime
    total_script_took   = fullcycle_endtime - refresh_end_time

    with open(path, 'a') as csvfile:
        log_writer = csv.writer(csvfile)
        log_writer.writerow(['done', refresh_start_time, refresh_took.seconds/60, validate_took.seconds/60,
                             hard_dedup_took.seconds/60, total_script_took.seconds/60])
    csvfile.close()

def refresh_sqoot_data(last_refresh_time, indirectload=False, firsttime=False):
    '''
    Summary: Iterate through Sqoot's entire coupon payload and download and update accordingly.
    '''

    refresh_start_time = datetime.now(pytz.utc) # Use UTC time to compare & update coupon's 'last_modified' field
    request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
    }
    print "\nSQOOT DATA LOAD STARTING..", show_time()

    describe_section("ESTABLISHING CATEGORY DICTIONARY..", show_time())
    request_try = 1
    while True:
        try:
            categories_array = requests.get(SQOOT_API_URL + 'categories', params=request_parameters, timeout=5).json()['categories']
            request_try = 1
            break
        except:
            print "Request timed out after 5 seconds. Let's wait another 5 seconds and try again."
            time.sleep(5)
            request_try += 1
            print "Trying for the {} time...".format(request_try)
    categories_dict = establish_categories_dict(categories_array) # Returns a dict with child: parent categories
    reorganized_categories_array = reorganize_categories_list(categories_array) # list of dict with 'category_name', and 'category_slug'
    for category_dict in reorganized_categories_array:
        get_or_create_category(category_dict, categories_dict)

    # loading coupons and merchants
    describe_section("CHECKING THE LATEST DEAL DATA FROM SQOOT..", show_time())
    request_parameters['per_page'] = ITEMS_PER_PAGE
    while True:
        try:
            sqoot_active_deal_count = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()['query']['total']
            request_try = 1
            break
        except:
            print "Request timed out after 5 seconds. Let's wait another 5 seconds and try again."
            time.sleep(5)
            request_try += 1
            print "Trying for the {} time...".format(request_try)
    page_count = int(math.ceil(sqoot_active_deal_count / float(request_parameters['per_page'])))
    print '%s deals detected, estimating %s pages to iterate' % (sqoot_active_deal_count, page_count), show_time()

    describe_section("STARTING TO DOWNLOAD SQOOT DEALS..", show_time())
    # Since there's only one country & dealtype for all sqoot deals - no need to check it for each coupon
    country_model       = get_or_create_country()
    dealtype_model      = get_or_create_dealtype()

    sqoot_output_deals = None
    if indirectload:
        sqoot_output_deals = json.loads(open("sqoot_output.json","r").read())

    # for p in range(page_count):
    for p in range(100): # DEBUG!!!
        request_parameters['page'] = p + 1
        print "\n"
        print '## Fetching page {} out of {}...'.format(p + 1, page_count), show_time()
        print "\n"

        if indirectload:
            response_in_json = sqoot_output_deals[p]
        else:
            while True:
                try:
                    response_in_json = requests.get(SQOOT_API_URL + 'deals', params=request_parameters, timeout=5).json()
                    request_try = 1
                    break
                except:
                    print "Request timed out after 5 seconds. Let's wait another 5 seconds and try again."
                    time.sleep(5)
                    request_try += 1
                    print "Trying for the {} time...".format(request_try)

        active_coupon_ids = [] # List of sqoot coupon ids to hold all active deal ids per page, as set 'page' request_parameters.
        deals_data = response_in_json['deals']
        for deal_data in deals_data:
            sqoot_coupon_id = int(deal_data['deal']['id'])
            active_coupon_ids.append(sqoot_coupon_id)

            deal_last_updated = parse(deal_data['deal']['updated_at']+'+0000')
            if (not firsttime) and last_refresh_time and (deal_last_updated < last_refresh_time):
                continue

            try:
                is_online_bool = deal_data['deal']['online']
                merchant_data_dict = deal_data['deal']['merchant']

                # Note: Only retrieve if already exists: 'couponnetwork_model', 'category_model', 'merchantlocation_model'
                # Note: Update with the latest data from sqoot even if exists: 'merchant_model', 'coupon_model'
                # 'shortcut=True' is given for get_or_create_category() since all categories were 'get_or_create'd above.
                couponnetwork_model      = get_or_create_couponnetwork(deal_data['deal'])
                category_model           = get_or_create_category(deal_data['deal'], categories_dict, shortcut=True)
                merchant_model, merchant_created = get_or_create_merchant(merchant_data_dict)
                merchantlocation_model   = get_or_create_merchantlocation(merchant_data_dict, merchant_model, is_online_bool)
                coupon_model             = get_or_create_coupon(deal_data['deal'], merchant_model, category_model, dealtype_model,
                                                                country_model, couponnetwork_model, merchantlocation_model)

                if merchant_created:
                    print 'DEDUP-SOFT: ...newly created merchant for this coupon, so moving on...', show_time() # DEBUG!!!
                    pass
                else:
                    print 'DEDUP-SOFT: coupon %s' % coupon_model.embedly_title, show_time()
                    dedup_scoot_data_soft(coupon_model)

                print '-' * 60
            except:
                print_stack_trace()
        Coupon.all_objects.filter(ref_id_source='sqoot', ref_id__in=active_coupon_ids).update(last_modified=datetime.now(pytz.utc))
    refresh_end_time = datetime.now(pytz.utc)
    return refresh_start_time, refresh_end_time

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

def clean_out_sqoot_data(refresh_start_time):
    '''
    Summary: Internal garbage collection cycle that finds and soft-delete all
             irrelevant and stale local coupons and merchants.
    Note:
    * First find all true duplicate deals and soft-delete them
    * Second, find all folded deals (i.e. is_duplicate=True, related_deal__isnull=True)
      that are stale (either expired or inactive, both implied and confirmed), and soft-delete them
    * Third, find all unique deals that are stale, check for folded deals (if so, reassign)
      and soft-delete them.
    * Fourth, find all inactive merchants (no active deals), and soft-delete them.
    '''

    describe_section("clean_out_sqoot_data IS BEGINNING..", show_time())
    affected_merchant_list = [] # collect a list of merchant pks whose coupons are being soft-deleted

    # First
    true_duplicate_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                     is_duplicate=True, related_deal__isnull=True)
    affected_merchant_list += [c.merchant.pk for c in true_duplicate_deals]
    true_duplicate_deals.update(is_deleted=True)

    # Second
    folded_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                             is_duplicate=True, related_deal__isnull=False)
    affected_merchant_list += [c.merchant.pk for c in folded_deals]
    folded_deals.filter(last_modified__lt=refresh_start_time).update(status='implied-inactive', is_deleted=True)
    folded_deals.filter(status='confirmed-inactive').update(is_deleted=True)
    folded_deals.filter(end__lt=datetime.now(pytz.utc)).update(is_deleted=True)

    # Third (Second -> Third; the order matters)
    non_dup_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False, is_duplicate=False)\
                                      .filter(Q(last_modified__lt=refresh_start_time)\
                                            | Q(status='confirmed-inactive')\
                                            | Q(end__lt=datetime.now(pytz.utc)))
    affected_merchant_list += [c.merchant.pk for c in non_dup_deals]
    deals_with_folded_deals = [c.pk for c in non_dup_deals if Coupon.all_objects.filter(related_deal=c, is_deleted=False).count() != 0]
    for i in deals_with_folded_deals:
        reassign_representative_deal(Coupon.all_objects.get(pk=i))
    non_dup_deals.filter(last_modified__lt=refresh_start_time).update(status='implied-inactive', is_deleted=True)
    non_dup_deals.filter(status='confirmed-inactive').update(is_deleted=True)
    non_dup_deals.filter(end__lt=datetime.now(pytz.utc)).update(is_deleted=True)

    # Fourth
    affected_merchant_list = list(set(affected_merchant_list))
    inactive_merchant_list = []
    for m_pk in affected_merchant_list:
        miq = Merchant.all_objects.get(pk=m_pk) # miq == merchant-in-question
        num_of_active_coupons_from_miq = Coupon.all_objects.filter(ref_id_source='sqoot',\
                                                                   merchant=miq, is_deleted=False).count()
        if num_of_active_coupons_from_miq:
            continue
        else:
            inactive_merchant_list.append(miq.pk)
    Merchant.all_objects.filter(pk__in=inactive_merchant_list).update(is_deleted=True)

    cleanout_endtime = datetime.now(pytz.utc)
    return cleanout_endtime

def validate_sqoot_data(refresh_start_time=None, pulseonly=False, stoptime=None):
    '''
    Summary: Fetch a deal page and validate deal information and availabilty.
    '''
    describe_section("validate_sqoot_data IS BEGINNING..", show_time())
    all_active_deals_on_display = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                            is_duplicate=False, online=False)\
                                                    .filter(Q(status='unconfirmed') | Q(status='considered-active'))
    print "...VALIDATING", len(all_active_deals_on_display), "DEALS:"

    validators = Pool(15)
    check_list = all_active_deals_on_display
    validators.map(go_validate, zip(list(check_list), repeat(refresh_start_time), repeat(pulseonly)))

    print "FINISHED VALIDATING....", show_time()
    validate_endtime = datetime.now(pytz.utc)
    return validate_endtime

def go_validate((coupon_model, refresh_start_time, pulseonly)):
    try:
        print show_time(), coupon_model.directlink

        sqoot_url = coupon_model.directlink
        is_bad_link, response = fetch_page(sqoot_url)
        if is_bad_link:
            # confirmed_inactive_list.append(coupon_model.pk)
            Coupon.all_objects.filter(pk=coupon_model.pk).update(status='confirmed-inactive')
            return

        is_deal_dead = check_if_deal_dead(coupon_model, response, sqoot_url)
        if is_deal_dead:
            # confirmed_inactive_list.append(coupon_model.pk)
            Coupon.all_objects.filter(pk=coupon_model.pk).update(status='confirmed-inactive')
        else:
            # considered_active_list.append(coupon_model.pk)
            Coupon.all_objects.filter(pk=coupon_model.pk).update(status='considered-active')

        if pulseonly:
            return
        elif refresh_start_time and (refresh_start_time > coupon_model.date_added):
            # Data check only the newly added deals.
            return
        else:
            confirm_or_correct_deal_data(coupon_model, response)
    except:
        print_stack_trace()

def dedup_sqoot_data_hard(refresh_start_time=None, firsttime=False):
    '''
    Summary: Further dedup coupons by checking deals under common fields vs. their locations.
    '''
    describe_section("dedup_sqoot_data_hard IS BEGINNING..", show_time())

    # Grab all active deals on display to users for deduping.
    deals_to_dedup = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                               is_duplicate=False, online=False, status='considered-active')
    if (not firsttime) and refresh_start_time:
        # If not first time, further filter down to only the newly added unique deals for deduping.
        deals_to_dedup = deals_to_dedup.filter(date_added__gt=refresh_start_time)

    crosscheck_by_field(deals_to_dedup, 'coupon_directlink')
    crosscheck_by_field(deals_to_dedup, 'merchant_name')
    print "FINISHED DEDUPING HARD....", show_time()

    hard_dedup_endtime = datetime.now(pytz.utc)
    return hard_dedup_endtime
