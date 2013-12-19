import string
import random

from tastypie.resources import ModelResource
# from geopy import geocoders
from geopy.distance import distance as geopy_distance
from haystack.query import SearchQuerySet
from haystack.utils.geo import Point, D
from elasticsearch import Elasticsearch

from core.util import print_stack_trace
from core.models import Coupon, Category

class MobileResource(ModelResource):

    def __init__(self, *args, **kwargs):
        # super(MobileResource, self).save(*args, **kwargs) # didn't work
        super(MobileResource, self).__init__()
        self.es = Elasticsearch()
        self.available_categories_list = [c.name for c in Category.objects.all()]
        self.sanitized_categories_list = [c for c in self.available_categories_list if self.check_if_should_exclude(c)]

    def deals_return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        params_dict = request.GET
        params_keys = params_dict.keys()

        try:
            location_param = params_dict['location']
            lat_lng_in_list = location_param.split(',')
            lat = float(lat_lng_in_list[0])
            lng = float(lat_lng_in_list[1])
        except:
            response = {
                'error': {'message': "You must supply a valid user location information."}
            }
            return self.create_response(request, response)

        try:
            id_param = params_dict['id']
        except:
            response = {
                'error': {'message': "You must supply a valid user uuid."}
            }
            return self.create_response(request, response)

        radius = D(mi=float(params_dict['radius'])) if 'radius' in params_keys else D(mi=10)
        user_pnt = Point(lng, lat)
        # sqs = SearchQuerySet().filter(django_ct='core.coupon', coupon_source='sqoot', online=False, is_duplicate=False).dwithin('merchant_location', user_pnt, radius).distance('merchant_location', user_pnt).order_by('distance')
        sqs = SearchQuerySet().filter(django_ct='core.coupon', coupon_source='sqoot', online=False).dwithin('merchant_location', user_pnt, radius).distance('merchant_location', user_pnt).order_by('distance')

        if 'query' in params_keys:
            query = params_dict['query']
            sqs_by_query = SearchQuerySet().filter(mobilequery=query)
            sqs = sqs.__and__(sqs_by_query)

            # Prepare for 'localindex' api service
            self.create_localinfo_index_if_doesnt_exist()
            matched_category_indices = [i for i, s in enumerate(self.available_categories_list) if query.lower() in s.lower()]
            matched_category_names = [self.available_categories_list[i] for i in matched_category_indices]
            self.index_it_in_localinfo_populars(id_param, location_param, string.capwords(query), matched_category_names)

        if 'category_slugs' in params_keys:
            category_slugs_list = params_dict['category_slugs'].split(',')
            sqs_by_category = SearchQuerySet()
            for c in category_slugs_list:
                sqs_by_category = sqs_by_category.filter_or(category_slugs=c.strip())
            sqs = sqs.__and__(sqs_by_category)

        if 'provider_slugs' in params_keys:
            provider_slugs_list = params_dict['provider_slugs'].split(',')
            sqs_by_provider = SearchQuerySet()
            for p in provider_slugs_list:
                sqs_by_provider = sqs_by_provider.filter_or(provider_slugs=p.strip())
            sqs = sqs.__and__(sqs_by_provider)

        updated_after = params_dict['updated_after'] if 'updated_after' in params_keys else None
        per_page = int(params_dict['per_page']) if 'per_page' in params_keys else 20
        page = int(params_dict['page']) if 'page' in params_keys else 1
        start_point = (page - 1) * per_page
        end_point = page * per_page

        deals = []

        for sqs_coupon_obj in sqs[start_point:end_point]:
            # coupon = Coupon.all_objects.get(pk=int(sqs_coupon_obj.pk))
            coupon = Coupon.objects.get(pk=int(sqs_coupon_obj.pk))
            merchant = coupon.merchant
            merchant_location = coupon.merchant_location
            dist_to_user = geopy_distance((user_pnt.y, user_pnt.x), (merchant_location.geometry.y, merchant_location.geometry.x)).miles
            coupon_network = coupon.coupon_network

            deal_description = coupon.description
            related_coupons = coupon.coupon_set.all()
            deal_description = coupon.description
            if len(related_coupons) is not 0:
                deal_description = deal_description if coupon.description else ""
                deal_description += "\n\nFind {} more similar deal(s) from this vendor on {}!".format(len(related_coupons), coupon_network.name)
                # for c in related_coupons[:5]:
                #     deal_description += c.embedly_title + "\n"

            each_deal = {'deal':
                {
                    'id':                   int(coupon.ref_id),
                    'title':                coupon.embedly_title,
                    'short_title':          coupon.embedly_description,
                    'description':          deal_description,
                    'fine_print':           coupon.restrictions,
                    'number_sold':          None,
                    'url':                  coupon.link,
                    'untracked_url':        coupon.directlink,
                    'price':                coupon.price,
                    'value':                coupon.listprice,
                    'discount_amount':      coupon.discount,
                    'discount_percentage':  float(coupon.percent) / 100,
                    'commission':           None,
                    'provider_name':        coupon_network.name,
                    'provider_slug':        coupon_network.code,
                    'category_name':        ', '.join([c.name for c in coupon.categories.all()]),
                    'category_slug':        ', '.join([c.code for c in coupon.categories.all()]),
                    'image_url':            coupon.embedly_image_url,
                    'online':               coupon.online,
                    'expires_at':           coupon.end,
                    'created_at':           coupon.start,
                    'updated_at':           coupon.lastupdated,
                    'is_duplicate':         coupon.is_duplicate,
                    'merchant': {
                        'id':               int(merchant.ref_id),
                        'name':             merchant.name,
                        'address':          merchant_location.address,
                        'locality':         merchant_location.locality,
                        'region':           merchant_location.region,
                        'postal_code':      merchant_location.postal_code,
                        'country':          "United States",
                        'country_code':     "US",
                        'latitude':         merchant_location.geometry.y,
                        'longitude':        merchant_location.geometry.x,
                        'dist_to_user_mi':  dist_to_user,
                        'url':              merchant.link,
                    }
                }
            }
            deals.append(each_deal)

        query = {
            'total':                    len(sqs),
            'page':                     page,
            'per_page':                 per_page,
            'query':                    query if 'query' in params_keys else None,
            'location': {
                 'latitude':            lat,
                 'longitude':           lng,
            },
            'radius':                   float(params_dict['radius']) if 'radius' in params_keys else 10,
            'online':                   False,
            'category_slugs':           category_slugs_list if 'category_slugs' in params_keys else None,
            'provider_slugs':           provider_slugs_list if 'provider_slugs' in params_keys else None,
            'updated_after':            updated_after,
        }

        response = {
            'query': query,
            'deals': deals,
        }

        return self.create_response(request, response)


    def localinfo_return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.create_localinfo_index_if_doesnt_exist()

        params_dict = request.GET
        try:
            location_param = params_dict['location']
        except:
            response = {
                'error': {'message': "You must supply a valid user location information."}
            }
            return self.create_response(request, response)

        default_radius_filter = '5mi'
        filters = {
            "query": {
                "filtered" : {
                    "query" : {
                        "match_all" : {}
                    },
                    "filter" : {
                        "geo_distance" : {
                            "distance" : default_radius_filter,
                            "location" : location_param
                        }
                    }
                }
            },
            "facets": {
                "search_keyword" : {
                    "terms" : {
                        "field" : "search_keyword",
                        "order" : "count"
                    }
                },
                "search_category" : {
                    "terms" : {
                        "field" : "search_category",
                        "order" : "count"
                    }
                }
            }
        }

        self.create_localinfo_index_if_doesnt_exist()
        res = self.es.search(index="localinfo", doc_type='populars', body=filters)
        popular_category_list_raw = res['facets']['search_category']['terms']
        popular_nearby_list_raw = res['facets']['search_keyword']['terms']

        base_response = {
            "default_image": "http://s3.amazonaws.com/pushpennyapp/default-placeholder.jpg",
            "search_categories": []
        }
        popular_category_sub_structure = {
            "name": "Popular Categories",
            "list": []
        }
        popular_nearby_sub_structure = {
            "name": "Popular Nearby",
            "list": []
        }

        # Always show 'popular categories' based on either user search history or random suggestions.
        # Always include 2 randomly selected categories to avoid self-enforcing popular categories
        max_total_categories = 6
        max_searched_categories = 4
        for c in popular_category_list_raw[:max_searched_categories]:
            if c['count'] < 100:
                break
            else:
                popular_category = self.return_popular_something_insert(c['term'])
                popular_category_sub_structure['list'].append(popular_category)

        while True:
            popular_categories_so_far = [c['name'] for c in popular_category_sub_structure['list']]
            if len(popular_categories_so_far) >= max_total_categories:
                break
            random_pick = random.sample(self.sanitized_categories_list, 1)[0]
            if random_pick not in popular_categories_so_far:
                 popular_category = self.return_popular_something_insert(random_pick)
                 popular_category_sub_structure['list'].append(popular_category)
        base_response['search_categories'].append(popular_category_sub_structure)

        # Show 'popular nearby' based on user search history ONLY IF 100 or above history;
        # 'nearby' and 'keyword' used interchangeably.
        max_nearbys = 5
        for kw in popular_nearby_list_raw[:max_nearbys]:
            if kw['count'] < 100:
                break
            else:
                popular_nearby = self.return_popular_something_insert(kw['term'])
                popular_nearby_sub_structure['list'].append(popular_nearby)
        if popular_nearby_sub_structure['list']:
            base_response['search_categories'].append(popular_nearby_sub_structure)

        # only for debugging purposes below
        base_response['elasticsearch_res'] = res

        response = base_response
        return self.create_response(request, response)

    ############################################################################################
    # Helper Methods
    ############################################################################################

    def create_localinfo_index_if_doesnt_exist(self):
        if not self.es.indices.exists(index='localinfo'):
            try:
                settings_and_mappings = {
                    "mappings": {
                        "populars": {
                            "properties": {
                                "user_uuid": {"type": "string"},
                                "location": {"type": "geo_point"},
                                "search_keyword": {"type": "string"},
                                "search_category": {"type": "string"}
                            }
                        }
                    }
                }
                self.es.indices.create(index='localinfo', body=settings_and_mappings)
            except:
                print_stack_trace()

    def index_it_in_localinfo_populars(self, user_uuid, location, search_keyword, search_category):
        localinfo_data_capture = {
            'user_uuid': user_uuid,
            'location': location,
            'search_keyword': search_keyword,
            'search_category': search_category if search_category else None
        }
        self.es.index(index="localinfo", doc_type='populars', body=localinfo_data_capture)

    def check_if_should_exclude(self, category):
        categories_to_exclude_list = ['Jewish', 'Gay', 'Special Interest']
        if category in categories_to_exclude_list:
            return False
        else:
            return True

    def return_popular_something_insert(self, category_or_keyword):
        popular_something = {
            "image": None,
            "name": category_or_keyword
        }
        return popular_something


