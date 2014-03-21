# -*- coding: utf-8 -*-
from copy import copy
import math
import time
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
from core.util import print_stack_trace, handle_exceptions
from core.util.sqootutils import (reorganize_categories_list, establish_categories_dict,
                                  get_or_create_category, get_or_create_dealtype, get_or_create_country,
                                  fetch_page, check_if_deal_dead, reassign_representative_deal,
                                  describe_section, show_time, crosscheck_by_field,
                                  read_sqoot_log, write_sqoot_log, reset_db_queries, update_coupon_data)

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
        make_option('--cleanout', action='store_true', dest='cleanout', default=False, help='cleanout'),
        make_option('--fullcycle', action='store_true', dest='fullcycle', default=False, help='fullcycle'),
        make_option('--directload', action='store_true', dest='directload', default=False, help='directload'),
        make_option('--indirectload', action='store_true', dest='indirectload', default=False, help='indirectload'),
        make_option('--validate', action='store_true', dest='validate', default=False, help='validate'),
        make_option('--deduphard', action='store_true', dest='deduphard', default=False, help='deduphard'),
    )

    def handle(self, *args, **options):
        firsttime = True if 'firsttime' in args else False
        if options.get('fullcycle', None):
            run_thru_full_cycle(args)

        if options.get('directload', None):
            refresh_sqoot_data(firsttime=firsttime)

        if options.get('cleanout', None):
            clean_out_sqoot_data(firsttime=firsttime)

        if options.get('indirectload', None):
            refresh_sqoot_data(indirectload=True, firsttime=firsttime)

        if options.get('validate', None):
            pulseonly = True if 'pulseonly' in args else False
            validate_sqoot_data(firsttime=firsttime, pulseonly=pulseonly)

        if options.get('deduphard', None):
            dedup_sqoot_data_hard(firsttime=firsttime)


@handle_exceptions
def run_thru_full_cycle(args):
    '''
    Summary: A wrapper function to run daily refresh, validate, dedup and clean functions consecutively.

    Note: Takes 'firsttime' argument.
    '''
    firsttime = True if 'firsttime' in args else False
    describe_section("FULLCYCLE STARTING..", show_time())
    refresh_sqoot_data(firsttime=firsttime)
    clean_out_sqoot_data(firsttime=firsttime)
    validate_sqoot_data(firsttime=firsttime)
    dedup_sqoot_data_hard(firsttime=firsttime)
    describe_section("ALL DONE!! :)", show_time())


@handle_exceptions
def refresh_sqoot_data(indirectload=False, firsttime=False):
    '''
    Summary: Iterate through Sqoot's entire coupon payload and download and update accordingly.
    '''
    last_refresh_start_time = read_sqoot_log('refresh')
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

    for p in range(page_count):
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
            if (not firsttime) and last_refresh_start_time and (deal_last_updated < last_refresh_start_time):
                continue

            is_online_bool = deal_data['deal']['online']
            merchant_data_dict = deal_data['deal']['merchant']
            update_coupon_data(deal_data, categories_dict, merchant_data_dict, is_online_bool, dealtype_model, country_model)
            print '-' * 60

            reset_db_queries()

        Coupon.all_objects.filter(ref_id_source='sqoot', ref_id__in=active_coupon_ids).update(last_modified=datetime.now(pytz.utc))
        refresh_end_time = datetime.now(pytz.utc)

    write_sqoot_log('refresh', refresh_start_time, refresh_end_time)
    print '\n'
    print "GOOD NEWS! refresh_sqoot_data IS ALL DONE AND LOGGING IT", show_time()
    reset_db_queries()
    return refresh_start_time, refresh_end_time


@handle_exceptions
def clean_out_sqoot_data(firsttime=False):
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
    from core.signals import delete_object

    last_refresh_start_time = read_sqoot_log('refresh') if firsttime == False else None
    cleanout_start_time = datetime.now(pytz.utc)
    describe_section("clean_out_sqoot_data IS BEGINNING..", show_time())
    affected_merchant_list = [] # collect a list of merchant pks whose coupons are being soft-deleted

    # First
    true_duplicate_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                     is_duplicate=True, related_deal__isnull=True)
    deals_for_update = copy(true_duplicate_deals)
    affected_merchant_list += [c.merchant.pk for c in true_duplicate_deals]
    true_duplicate_deals.update(is_deleted=True)
    # triggering deletion of duplicated coupons from search index
    for coupon in deals_for_update:
        print 'Deleted %s' % coupon.id
        delete_object.send(sender=Coupon, instance=coupon)
    print '~*~*~*~*~*~*~*~*~* First finished ~*~*~*~*~*~*~*~*~*'

    # Second
    if last_refresh_start_time:
        folded_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                 is_duplicate=True, related_deal__isnull=False)\
                                         .filter(Q(last_modified__lt=last_refresh_start_time)\
                                               | Q(status='confirmed-inactive')\
                                               | Q(end__lt=datetime.now(pytz.utc)))
    else:
        folded_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                 is_duplicate=True, related_deal__isnull=False)\
                                         .filter(Q(status='confirmed-inactive')\
                                               | Q(end__lt=datetime.now(pytz.utc)))
    affected_merchant_list += [c.merchant.pk for c in folded_deals]

    deals_to_signal = []
    deals_to_signal += [c.pk for c in folded_deals.filter(Q(status='confirmed-inactive')
                                                        | Q(end__lt=datetime.now(pytz.utc)))]
    if last_refresh_start_time:
        deals_to_signal += [c.pk for c in folded_deals.filter(last_modified__lt=last_refresh_start_time)]
        folded_deals.filter(last_modified__lt=last_refresh_start_time).update(status='implied-inactive', is_deleted=True)
    folded_deals.filter(status='confirmed-inactive').update(is_deleted=True)
    folded_deals.filter(end__lt=datetime.now(pytz.utc)).update(is_deleted=True)

    deals_to_signal = list(set(deals_to_signal))
    for coupon in Coupon.all_objects.filter(pk__in=deals_to_signal):
        print 'Deleted %s' % coupon.id
        delete_object.send(sender=Coupon, instance=coupon)
    print '~*~*~*~*~*~*~*~*~* Second finished ~*~*~*~*~*~*~*~*~*'

    # Third (Second -> Third; the order matters)
    if last_refresh_start_time:
        non_dup_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False, is_duplicate=False)\
                                          .filter(Q(last_modified__lt=last_refresh_start_time)\
                                                | Q(status='confirmed-inactive')\
                                                | Q(end__lt=datetime.now(pytz.utc)))
    else:
        non_dup_deals = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False, is_duplicate=False)\
                                          .filter(Q(status='confirmed-inactive')\
                                                | Q(end__lt=datetime.now(pytz.utc)))
    affected_merchant_list += [c.merchant.pk for c in non_dup_deals]
    deals_with_folded_deals = [c.pk for c in non_dup_deals if Coupon.all_objects.filter(related_deal=c, is_deleted=False).count() != 0]
    for i in deals_with_folded_deals:
        reassign_representative_deal(Coupon.all_objects.get(pk=i))

    deals_to_signal = []
    deals_to_signal += [c.pk for c in non_dup_deals.filter(Q(status='confirmed-inactive')
                                                         | Q(end__lt=datetime.now(pytz.utc)))]
    if last_refresh_start_time:
        deals_to_signal += [c.pk for c in non_dup_deals.filter(last_modified__lt=last_refresh_start_time)]
        non_dup_deals.filter(last_modified__lt=last_refresh_start_time).update(status='implied-inactive', is_deleted=True)
    non_dup_deals.filter(status='confirmed-inactive').update(is_deleted=True)
    non_dup_deals.filter(end__lt=datetime.now(pytz.utc)).update(is_deleted=True)

    deals_to_signal = list(set(deals_to_signal))
    for coupon in Coupon.all_objects.filter(pk__in=deals_to_signal):
        print 'Deleted %s' % coupon.id
        delete_object.send(sender=Coupon, instance=coupon)
    print '~*~*~*~*~*~*~*~*~* Third finished ~*~*~*~*~*~*~*~*~*'

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
    cleanout_end_time = datetime.now(pytz.utc)
    write_sqoot_log('cleanout', cleanout_start_time, cleanout_end_time)
    print '\n'
    print "GOOD NEWS! cleanout_sqoot_data IS ALL DONE AND LOGGING IT", show_time()
    reset_db_queries()


@handle_exceptions
def validate_sqoot_data(firsttime=False, pulseonly=False):
    '''
    Summary: Fetch a deal page and validate deal information and availabilty.
    '''

    last_validate_end_time = read_sqoot_log('validate')
    validate_start_time = datetime.now(pytz.utc)
    describe_section("validate_sqoot_data IS BEGINNING..", show_time())
    all_active_deals_on_display = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                                            is_duplicate=False, online=False)\
                                                    .filter(Q(status='unconfirmed') | Q(status='considered-active'))
    print "...VALIDATING", len(all_active_deals_on_display), "DEALS:"

    validators = Pool(15)
    validators.map(go_validate, zip(list(all_active_deals_on_display), repeat(last_validate_end_time), repeat(firsttime), repeat(pulseonly)))

    print "FINISHED VALIDATING....", show_time()

    validate_end_time = datetime.now(pytz.utc)
    write_sqoot_log('validate', validate_start_time, validate_end_time)
    print '\n'
    print "GOOD NEWS! validate_sqoot_data IS ALL DONE AND LOGGING IT", show_time()
    reset_db_queries()


def go_validate((coupon_model, last_validate_end_time, firsttime, pulseonly)):
    from core.signals import update_object
    try:
        print show_time(), coupon_model.directlink

        sqoot_url = coupon_model.directlink
        is_bad_link, response = fetch_page(sqoot_url)
        if is_bad_link:
            coupon_model.status='confirmed-inactive'
            coupon_model.save()
            handle_exceptions(update_object.send(sender=Coupon, instance=coupon_model))
            return

        is_deal_dead = check_if_deal_dead(coupon_model, response, sqoot_url)
        if is_deal_dead:
            coupon_model.status='confirmed-inactive'
        else:
            coupon_model.status='considered-active'

        coupon_model.save()
        handle_exceptions(update_object.send(sender=Coupon, instance=coupon_model))
        reset_db_queries()

        # Note: Commenting out address/category correction logic (not implemented yet)
        # if firsttime:
        #     confirm_or_correct_deal_data(coupon_model, response)
        # else:
        #     if pulseonly:
        #         return
        #     if last_validate_end_time and (last_validate_end_time > coupon_model.date_added):
        #         return # Data check only the newly added deals.
        #     confirm_or_correct_deal_data(coupon_model, response)
    except:
        print_stack_trace()

@handle_exceptions
def dedup_sqoot_data_hard(firsttime=False):
    '''
    Summary: Further dedup coupons by checking deals under common fields vs. their locations.
    '''
    last_deduphard_end_time = read_sqoot_log('deduphard')
    deduphard_start_time = datetime.now(pytz.utc)

    describe_section("dedup_sqoot_data_hard IS BEGINNING..", show_time())

    # Grab all active deals on display to users for deduping.
    deals_to_dedup = Coupon.all_objects.filter(ref_id_source='sqoot', is_deleted=False,
                                               is_duplicate=False, online=False, status='considered-active')
    if (not firsttime) and last_deduphard_end_time:
        # If not first time, further filter down to only the newly added unique deals for deduping.
        deals_to_dedup = deals_to_dedup.filter(date_added__gt=last_deduphard_end_time)

    crosscheck_by_field(deals_to_dedup, 'coupon_directlink')
    crosscheck_by_field(deals_to_dedup, 'merchant_name')
    print "FINISHED DEDUPING HARD....", show_time()

    deduphard_end_time = datetime.now(pytz.utc)
    write_sqoot_log('deduphard', deduphard_start_time, deduphard_end_time)
    print '\n'
    print "GOOD NEWS! dedup_sqoot_data_hard IS ALL DONE AND LOGGING IT", show_time()
    reset_db_queries()
