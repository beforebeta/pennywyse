import requests
import random
from django.conf import settings
from django.template.defaultfilters import slugify
from .sample_data_feed import top_50_us_cities_dict, sample_query_strings

request_parameters = {
        # 'api_key': settings.SQOOT_PUBLIC_KEY,
        'api_key': 'xhtihz',
        'per_page': 100,
        'radius': 10,
        'order': 'distance'
    }

SQOOT_API_URL = "http://api.sqoot.com/v2/"
LOCAL_API_URL = "http://localhost:8000/v3/"
MATCH_THRESHOLD = 0.6

# def test_local_deals_api_page_one_vs_sqoot():
#     categories_list = get_categories_list()
#     picked_category = random.sample(categories_list, 1)[0]
#     request_parameters['category_slugs'] = slugify(picked_category)
#     for location in top_50_us_cities_dict.values():
#         request_parameters['location'] = location
#         local_response, sqoot_response = fetch_local_and_sqoot_responses(request_parameters)
#         sqoot_deals_list = sqoot_response['deals']
#         local_deals_list = local_response['deals']
#         if len(sqoot_deals_list) == 0:
#             continue
#         else:
#             yield check_deals_match_vs_threshold, local_deals_list, sqoot_deals_list

def test_local_deals_response_ordered_by_distance():
    picked_location = random.sample(top_50_us_cities_dict.values(), 1)
    request_parameters['location'] = picked_location
    local_response, sqoot_response = fetch_local_and_sqoot_responses(request_parameters)
    distance_list = [int(deal['deal']['merchant']['dist_to_user_mi']) for deal in local_response['deals']]
    assert distance_list == sorted(distance_list)


##################################################################################################
# Helper Methods
##################################################################################################

def check_deals_match_vs_threshold(local_deals_list, sqoot_deals_list):
    # default 'per_page' is 20 for both sqoot and local api
    local_deal_ids_list = [deal_dict['deal']['id'] for deal_dict in local_deals_list]
    sqoot_deal_ids_list = [deal_dict['deal']['id'] for deal_dict in sqoot_deals_list]
    common_deals = list(set(local_deal_ids_list) & set(sqoot_deal_ids_list))
    common_deal_ratio = float(len(common_deals)) / float(len(sqoot_deal_ids_list))
    assert common_deal_ratio > MATCH_THRESHOLD


def fetch_local_and_sqoot_responses(request_parameters):
    local_response = requests.get(LOCAL_API_URL + 'deals', params=request_parameters).json()
    sqoot_response = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()
    return local_response, sqoot_response

def get_categories_list():
    sqoot_categories = requests.get(SQOOT_API_URL + 'categories', params=request_parameters).json()['categories']
    categories_list = [category['category']['name'] for category in sqoot_categories]
    return categories_list