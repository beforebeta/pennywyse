import json
import requests
from django.http import HttpResponse
from core.models import Category

def deals(request):
    API_URL = "http://api.sqoot.com/v2/deals"
    parameters = {}
    for item in request.GET.items():
        parameters[item[0]] = item[1]
    parameters['per_page'] = 100
    query = request.GET.get("query","")

    response = {}
    if query:
        query_response = requests.get(API_URL, params=parameters).json()

        try:
            checked_category = Category.all_objects.get(ref_id_source='sqoot', name__iexact=query.lower())
        except:
            checked_category = None

        if checked_category:
            try:
                del parameters["query"]
            except:
                pass
            finally:
                parameters["category_slugs"] = checked_category.code
            category_response = requests.get(API_URL, params=parameters).json()

            response = {'deals': query_response['deals'], 'query': {}}
            query_response_deal_ids_list = [a['deal']['id'] for a in query_response['deals']]
            duplicate_deals = []
            for deal in category_response['deals']:
                deal_id_to_check = deal['deal']['id']
                if deal_id_to_check in query_response_deal_ids_list:
                    duplicate_deals.append(deal_id_to_check)
                else:
                    response['deals'].append(deal)
            response['query']['merged_total'] = len(response['deals'])
            response['query']['duplicates_removed'] = len(duplicate_deals)
            response['query']['duplicate_deals'] = duplicate_deals
        else:
            response = query_response
    else:
        response = requests.get(API_URL, params=parameters).json()
    return HttpResponse(json.dumps(response), mimetype='text/html; charset=utf-8;')

def localinfo(request):
    response = {
        "popular_categories": [],
        "popular_nearby":[ "Restaurants", "Spa", "Gym"]
    }
    for c in Category.all_objects.filter(ref_id_source='sqoot', parent__isnull=True):
        response["popular_categories"].append(
            {"name"     : c.name,
             "slug"     : c.code,
             "image"    : c.image
            }
        )
    return HttpResponse(json.dumps(response), mimetype='text/html; charset=utf-8;')
