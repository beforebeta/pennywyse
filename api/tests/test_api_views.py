import requests
import random
# from django.conf import settings
from api.tests.sample_data_feed import top_50_us_cities_dict, sample_query_strings
from django.template.defaultfilters import slugify

PUSHPENNY_API_URL = "http://api.pushpenny.com/v2/"
SQOOT_API_URL = "http://api.sqoot.com/v2/"

request_parameters = {
        # 'api_key': settings.SQOOT_PUBLIC_KEY,
        'api_key': 'xhtihz',
        'order': 'distance',
        'per_page': 100,
        'radius': 10,
    }

def test_deals_api_with_query_matching_category():
    categories_list = get_categories_list()
    for category in categories_list:
        request_parameters['query'] = category
        pushpenny_deals_list = requests.get(PUSHPENNY_API_URL + 'deals', params=request_parameters).json()['deals']

        sqoot_deals_list_with_query = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['deals']
        del request_parameters['query']
        request_parameters["category_slugs"] = slugify(category)
        sqoot_deals_list_with_cat_slug = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['deals']
        sqoot_deals_list = sqoot_deals_list_with_query + sqoot_deals_list_with_cat_slug
        yield check_if_deals_match, pushpenny_deals_list, sqoot_deals_list, True, category

def test_deals_api_with_query_not_matching_category():
    random_query_strings = random.sample(sample_query_strings, 30)
    for query in random_query_strings:
        request_parameters['query'] = query
        pushpenny_deals_list = requests.get(PUSHPENNY_API_URL + 'deals', params=request_parameters).json()['deals']
        sqoot_deals_list = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['deals']
        yield check_if_deals_match, pushpenny_deals_list, sqoot_deals_list, False, query

def test_deals_api_with_location():
    for city_name, location in top_50_us_cities_dict.iteritems():
        request_parameters['location'] = location
        pushpenny_deals_list = requests.get(PUSHPENNY_API_URL + 'deals', params=request_parameters).json()['deals']
        sqoot_deals_list = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['deals']
        yield check_if_deals_match, pushpenny_deals_list, sqoot_deals_list, False, city_name


sample_number_per_variable = 10
def test_with_all_above_the_above():
    full_categories_list = get_categories_list()
    select_categories_list = random.sample(full_categories_list, sample_number_per_variable)
    select_query_strings = random.sample(sample_query_strings, sample_number_per_variable)

    potential_search_queries = select_categories_list + select_query_strings
    select_locations = random.sample(top_50_us_cities_dict.values(), sample_number_per_variable)
    for location in select_locations:
        request_parameters['location'] = location
        for search_query in potential_search_queries:
            request_parameters['query'] = search_query
            pushpenny_deals_list = requests.get(PUSHPENNY_API_URL + 'deals', params=request_parameters).json()['deals']
            sqoot_deals_list = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['deals']
            if search_query in full_categories_list:
                del request_parameters['query']
                request_parameters["category_slugs"] = slugify(search_query)
                sqoot_deals_list_with_cat_slug = requests.get(SQOOT_API_URL + 'deals', params=request_parameters).json()['deals']
                sqoot_deals_list = sqoot_deals_list + sqoot_deals_list_with_cat_slug
                yield check_if_deals_match, pushpenny_deals_list, sqoot_deals_list, True, search_query
            else:
                yield check_if_deals_match, pushpenny_deals_list, sqoot_deals_list, False, search_query

##################################################################################################
# Helper Methods
##################################################################################################

def check_if_deals_match(pushpenny_deals_list, sqoot_deals_list, dedup_sqoot_bool, iteration_info):
    pushpenny_deal_ids_list = [deal_dict['deal']['id'] for deal_dict in pushpenny_deals_list]
    sqoot_deal_ids_list = [deal_dict['deal']['id'] for deal_dict in sqoot_deals_list]
    if dedup_sqoot_bool:
        sqoot_deal_ids_list = list(set(sqoot_deal_ids_list))
    assert sorted(pushpenny_deal_ids_list) == sorted(sqoot_deal_ids_list)

def get_categories_list():
    sqoot_categories = requests.get(SQOOT_API_URL + 'categories', params=request_parameters).json()['categories']
    categories_list = [category['category']['name'] for category in sqoot_categories]
    return categories_list