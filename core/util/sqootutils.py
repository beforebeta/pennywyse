from datetime import datetime
from dateutil.parser import parse
import requests
import time
import re
import os
import csv

import pytz
from fuzzywuzzy import fuzz
from BeautifulSoup import BeautifulSoup

from django.conf import settings
from django.db import reset_queries
from django.db.models import Max
from django.utils.html import strip_tags

from core.models import DealType, Category, Coupon, Merchant, Country, CouponNetwork, MerchantLocation
from core.util import print_stack_trace, handle_exceptions

EASTERN_TZ = pytz.timezone('US/Eastern')

SQOOT_LOG_PATH = os.path.join(settings.BASE_DIR, 'misc','logonly', 'sqootload_running_log.txt')

# Which stage: ['row to look for', 'column to look for']
LOOKUP_PER_STAGE = {'refresh':   ['refresh', 1],
                    'cleanout':   ['refresh', 1],
                    'validate':  ['validate', 2],
                    'deduphard': ['deduphard', 2]}

########## Table of Contents #########
# 1. Helper Methods - Data Gathering
# 2. Helper Methods - Data Intelligence
# 3. Helper Methods - Formatting
# 4. Helper Methods - Logging

#############################################################################################################
#
# 1. Helper Methods - Data Gathering
#
#############################################################################################################

def reorganize_categories_list(categories_array):
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
    try:
        if created:
            print show_time(), "CREATED   : merchant %s" % merchant_data_dict['name']
        else:
            print show_time(), "UPDATING  : merchant %s" % merchant_data_dict['name']
    except:
        pass

    merchant_model.link         = merchant_data_dict['url']
    merchant_model.directlink   = merchant_data_dict['url']
    merchant_model.is_deleted   = False
    merchant_model.save()
    return merchant_model, created

def get_or_create_category(each_deal_data_dict, categories_dict, shortcut=False):
    '''
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
        print "CREATED   : deal type 'local'"
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
        print 'CREATED   : country entry for USA'
        country_model.name = 'usa'
        country_model.save()
    return country_model

def get_or_create_couponnetwork(each_deal_data_dict):
    provider_slug = each_deal_data_dict['provider_slug']
    couponnetwork_model, created = CouponNetwork.objects.get_or_create(code=provider_slug)
    if created:
        try:
            print show_time(), 'CREATED   : coupon network %s' % each_deal_data_dict['provider_name']
        except:
            pass
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
        try:
            print show_time(), 'CREATED   : location %s, %s for merchant %s' % (merchant_data_dict['locality'], merchant_data_dict['address'],
                                                                                merchant_model.name)
        except:
            pass
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

    try:
        if created:
            print show_time(), 'CREATED   : coupon %s' % each_deal_data_dict['title']
        else:
            print show_time(), 'UPDATING  : coupon %s' % each_deal_data_dict['title']
    except:
        pass

    if merchantlocation_model:
        coupon_model.online              = each_deal_data_dict['online']
    else:
        try:
            print 'this coupon has no location model', ref_id
        except:
            pass
        coupon_model.online          = True

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

def fetch_page(sqoot_url, tries=1):
    '''
    Summary: Check if url is valid and return a boolean with a response.
    '''
    try:
        if not sqoot_url:
            return True, None
        response = requests.get(sqoot_url, timeout=5)
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


@handle_exceptions
def update_coupon_data(deal_data, categories_dict, merchant_data_dict, is_online_bool, dealtype_model, country_model):
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
        try:
            print 'DEDUP-SOFT: coupon %s' % coupon_model.embedly_title, show_time()
        except:
            pass
        dedup_scoot_data_soft(coupon_model)

#############################################################################################################
#
# 2. Helper Methods - Data Intelligence
#
#############################################################################################################

def crosscheck_by_field(deals_to_dedup, field_name):
    from core.signals import update_object
    duplicate_deals_list = [] # List of duplicate coupon pks.

    if field_name == 'coupon_directlink':
        field_list = list(set([d.directlink for d in deals_to_dedup]))
    elif field_name == 'merchant_name':
        field_list = list(set([d.merchant.name for d in deals_to_dedup]))
    else:
        return

    all_active_deals = len(deals_to_dedup)
    num_of_unique_fields = len(field_list)
    try:
        print "\n...Detected {} deals by '{}' field to dedup out of {} total active deals".format(num_of_unique_fields, field_name, all_active_deals), show_time()
    except:
        pass

    progress_count = 1
    clear_cache_timer = 1
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
                print show_time(), '({}/{}) DEDUP-HARD:'.format(progress_count, num_of_unique_fields), '...no duplicate, skipping...'
                progress_count += 1
                clear_cache_timer += 1
                continue

            try:
                print show_time(), '({}/{}) DEDUP-HARD:'.format(progress_count, num_of_unique_fields), 'all deals with {}=={}'.format(field_name, x)
            except:
                pass

            while True:
                current_count = same_looking_deals.count()
                if current_count == 1:
                    break
                else:
                    for c in same_looking_deals[1:current_count]:
                        if c.is_duplicate or (c.pk in duplicate_deals_list):
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
            progress_count += 1
            clear_cache_timer += 1
            if clear_cache_timer >= 100:
                duplicate_deals_list = list(set(duplicate_deals_list))
                Coupon.all_objects.filter(pk__in=duplicate_deals_list).update(is_duplicate=True)
		for coupon in Coupon.all_objects.filter(pk__in=duplicate_deals_list):
                    handle_exceptions(update_object.send(sender=Coupon, instance=coupon))
		    print 'Updated %s' % coupon.id
                duplicate_deals_list = []
                clear_cache_timer = 1
        except:
            try:
                print "!!!ERROR: field: {}".format(x)
            except:
                pass
            print_stack_trace()

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

    if location_one.postal_code.strip() == location_two.postal_code.strip():
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

def reassign_representative_deal(coupon_model):
    '''
    Summary: Scan folded deals and reassign a repr. deal out of them before removing the current rep.

    Note:
    * Look for an alternative rep. deal based on the best discount
    * This function assumes that coupon_model has folded deals (>0) under it.
    '''
    merchant_sqoot_id = coupon_model.merchant.ref_id
    candidates = Coupon.all_objects.filter(merchant__ref_id=merchant_sqoot_id, is_deleted=False)\
                                   .exclude(ref_id=coupon_model.ref_id)
    if len(candidates) == 0:
        return
    max_disc_percent = candidates.aggregate(Max('percent'))['percent__max']
    new_rep_deal = candidates.filter(percent=max_disc_percent)[0]
    new_rep_deal.is_duplicate = False
    new_rep_deal.related_deal = None
    new_rep_deal.save()
    candidates.exclude(pk=new_rep_deal.pk).update(related_deal=new_rep_deal)

@handle_exceptions
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


def reset_db_queries():
    if settings.DEBUG:
        reset_queries()


@handle_exceptions
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
    reset_db_queries()

#############################################################################################################
#
# 3. Helper Methods - Formatting
#
#############################################################################################################

def describe_section(message, current_time=None):
    print " "
    print "*~"*30
    print message, current_time

def show_time():
    timestamp = datetime.now(EASTERN_TZ)
    return "(@{t.hour}:{t.minute}:{t.second} on {t.month}/{t.day})".format(t=timestamp)

def get_date(raw_date_string):
    if raw_date_string:
        return parse(raw_date_string+'+0000')
    return None

def cleanse_address_text(address_string):
    address_crufts = ['Rd', 'Hwy', 'Dr', 'St', 'Ave', 'Blvd', 'Expy', 'Ln', 'E', 'S', 'W', 'N', 'Pkwy', 'Cir',\
                      'Road', 'Highway', 'Drive', 'Street', 'Avenue', 'Boulevard', 'Expressway', 'Lane', 'East', 'South', 'West', 'North', 'Parkway', 'Circle']
    address_broken_down = address_string.replace('.', '').split(' ')
    caught_crufts = [val for val in address_broken_down if val in address_crufts]
    for c in caught_crufts:
        address_broken_down.remove(c)
    clean_address = (' ').join(address_broken_down)
    clean_address = re.sub(r"(?<=\d)(st|nd|rd|th)\b", '', clean_address)
    return clean_address


#############################################################################################################
#
# 4. Helper Methods - Logging
#
#############################################################################################################



def read_sqoot_log(current_stage):
    row_to_lookup, column_to_lookup = LOOKUP_PER_STAGE[current_stage]

    try:
        f = open(SQOOT_LOG_PATH, 'r')
    except IOError:
        print_stack_trace()

    all_rows = f.readlines()
    if len(all_rows) == 1:
        f.close()
        return None
    else:
        last_ten_rows = all_rows[-10:]
        latest_runs_of_this_step = [r for r in last_ten_rows if r.replace('\r\n', '').split(',')[0] == row_to_lookup]
        if len(latest_runs_of_this_step) == 0:
            f.close()
            return None
        very_last_run = latest_runs_of_this_step[-1]
        timestamp_string = very_last_run.replace('\r\n', '').split(',')[column_to_lookup]
        timestamp_wanted = parse(timestamp_string)
        f.close()
        return timestamp_wanted

def write_sqoot_log(finished_stage, start_time, end_time):
    time_took = end_time - start_time

    try:
        with open(SQOOT_LOG_PATH, 'a') as csvfile:
            log_writer = csv.writer(csvfile)
            log_writer.writerow([finished_stage, start_time, end_time, time_took.seconds/60,])
        csvfile.close()
    except:
        print_stack_trace()
        print "^-- WARNING: Problem logging it: {}{}{}{}{}{}{}"\
                .format(finished_stage, ",", start_time, ",", end_time, ",", time_took.seconds/60)
