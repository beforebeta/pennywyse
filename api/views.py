import json
import requests
from django.http import HttpResponse
from core.models import Category

SQOOT_API_URL = "http://api.sqoot.com/v2/deals"

def deals(request):
    parameters = {}
    for k,v in request.GET.items():
        parameters[k] = v
    query = request.GET.get("query","")

    response = {}
    if query:
        query_response = requests.get(SQOOT_API_URL, params=parameters).json()

        try:
            checked_category = Category.all_objects.get(ref_id_source='sqoot', name__iexact=query.lower())
        except Category.DoesNotExist:
            try:
                checked_category = Category.all_objects.get(ref_id_source='sqoot', code__iexact=query.lower())
            except Category.DoesNotExist:
                checked_category = None

        if checked_category:
            try:
                del parameters["query"]
            except:
                pass
            finally:
                parameters["category_slugs"] = checked_category.code
            category_response = requests.get(SQOOT_API_URL, params=parameters).json()

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
        response = requests.get(SQOOT_API_URL, params=parameters).json()
    return HttpResponse(json.dumps(response), mimetype='application/json; charset=utf-8;')

def localinfo(request):
    #response = {
    #    "popular_categories"    : [],
    #    "popular_nearby"        :[ "Restaurants", "Spa", "Gym"],
    #    "default_image"         : "http://s3.amazonaws.com/pushpennyapp/default-placeholder.jpg"
    #}
    #for c in Category.all_objects.filter(ref_id_source='sqoot', parent__isnull=True):
    #    response["popular_categories"].append(
    #        {"name"     : c.name,
    #         "slug"     : c.code,
    #         "image"    : c.image
    #        }
    #    )
    response = {
        "default_image": "http://s3.amazonaws.com/pushpennyapp/default-placeholder.jpg",
        "search_categories": [
        {
            "name": "Popular Categories",
            "list": [
                {
                    "image": "http://s3.amazonaws.com/pushpennyapp/activities-events.jpg",
                    "name": "Activities & Events",
                },
                {
                    "image": "http://s3.amazonaws.com/pushpennyapp/retail-services.jpg",
                    "name": "Retail & Services",
                },
                {
                    "image": "http://s3.amazonaws.com/pushpennyapp/special-interest.jpg",
                    "name": "Special Interest",
                }
            ]
            },
            {
                "name": "Popular Nearby",
                "list": [
                {
                         "name": "Restaurants",
                         "image": None
                     },
                     {
                         "name": "Spa",
                         "image": "http://s3.amazonaws.com/pushpennyapp/health-beauty.jpg"
                     },
                     {
                         "name": "Gym",
                         "image": None
                     }
                 ]
             },
             {
                 "name": "Black Friday Deals",
                 "list": [
                     {
                         "name": "Black Friday",
                         "image": None
                     },
                     {
                         "name": "Thanksgiving",
                         "image": "http://s3.amazonaws.com/pushpennyapp/dining-nightlife.jpg"
                     }
                 ]
             }
         ]
    }
    return HttpResponse(json.dumps(response), mimetype='application/json; charset=utf-8;')