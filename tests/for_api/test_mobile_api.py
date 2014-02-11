import requests
from collections import Counter
from django.conf import settings
from .sample_data_feed import top_50_us_cities_dict

request_parameters = {
        'api_key': settings.SQOOT_PUBLIC_KEY,
        'per_page': 100,
        'radius': 100,
    }

PUSHPENNY_API_URL = "http://api.pushpenny.com/v2/"
MIN_DEAL_QUANTITY = 100
MAX_CONSEC_DUPS = 2 # Must be >1
MAX_TOTAL_DUPS = 4

##################################################################################################
# Tests for '/deals' end point
##################################################################################################

def test_mobile_api_in_service():
    api_response = fetch_api_response(request_parameters)
    assert api_response.status_code == 200

def test_enough_local_deals_available():
    for name, lat_lng in top_50_us_cities_dict.iteritems():
        request_parameters['location'] = lat_lng
        api_response = fetch_api_response(request_parameters)
        yield check_deals_quantity_above_threshold, api_response, MIN_DEAL_QUANTITY, name

def test_consec_dup_deals_minimized():
    # Check only the first page in each city.
    for name, lat_lng in top_50_us_cities_dict.iteritems():
        request_parameters['location'] = lat_lng
        api_response = fetch_api_response(request_parameters)
        yield check_consec_dups_within_threshold, api_response, MAX_CONSEC_DUPS, name

def test_total_dup_deals_minimized():
    # Check only the first page in each city.
    for name, lat_lng in top_50_us_cities_dict.iteritems():
        request_parameters['location'] = lat_lng
        api_response = fetch_api_response(request_parameters)
        yield check_total_dups_within_threshold, api_response, MAX_TOTAL_DUPS, name

##################################################################################################
# Helper Methods
##################################################################################################

def fetch_api_response(request_parameters):
    return requests.get(PUSHPENNY_API_URL + 'deals', params=request_parameters)

def check_deals_quantity_above_threshold(api_response, minimum_threshold, reference_string=None):
    num_of_total_available = api_response.json()['query']['total']
    assert num_of_total_available >= minimum_threshold

def check_consec_dups_within_threshold(api_response, maximum_threshold, reference_string=None):
    short_titles = [each['deal']['short_title'] for each in api_response.json()['deals']]
    allowed_consec_dups = (maximum_threshold - 1)

    consec_dups_detected = 0
    previous_deal_title = None
    for s in short_titles:
        if not previous_deal_title:
            previous_deal_title = s
            continue
        if s == previous_deal_title:
            consec_dups_detected += 1
            previous_deal_title = s
            if consec_dups_detected > allowed_consec_dups:
                break
        else:
            consec_dups_detected = 0
            previous_deal_title = s
    assert consec_dups_detected <= allowed_consec_dups

def check_total_dups_within_threshold(api_response, maximum_threshold, reference_string=None):
    short_titles = [each['deal']['short_title'] for each in api_response.json()['deals']]
    dup_deals_above_threshold = [k + " ->" + str(v) for k, v in Counter(short_titles).items() if v > maximum_threshold]
    assert len(dup_deals_above_threshold) == 0
