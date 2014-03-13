import string
import random
import copy
from datetime import datetime

from django.core.cache import cache

from tastypie.resources import ModelResource
from geopy.distance import distance as geopy_distance
from haystack.query import SearchQuerySet
from haystack.utils.geo import Point, D
from elasticsearch import Elasticsearch
import pytz

from core.util import print_stack_trace
from core.models import Category

class MobileResource(ModelResource):

    def __init__(self, *args, **kwargs):
        super(MobileResource, self).__init__()
        self.es = Elasticsearch()
        self.available_categories_list = [c.name for c in Category.objects.filter(ref_id_source='sqoot').only('name').all()]
        self.parent_categories_list    = ['Dining & Nightlife',
                                          'Activities & Events',
                                          'Shopping & Services',
                                          'Health & Beauty',
                                          'Fitness',
                                          # 'Special Interest', # Excluded
                                          # 'Product', # Excluded
                                         ]
        self.sanitized_categories_list = filter(self.check_if_should_exclude, self.available_categories_list)

    def deals_return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        params_dict = request.GET
        params_keys = params_dict.keys()
        location_param = params_dict.get('location', None)
        if not location_param:
            response = {
                'error': {'message': "You must supply a valid user location information."}
            }
            return self.create_response(request, response)

        lat_lng_in_list = location_param.split(',')
        lat, lng = map(float, lat_lng_in_list)

        id_param = params_dict.get('id', 'uuid')

        radius = D(mi=float(params_dict['radius'])) if 'radius' in params_keys else D(mi=10)
        user_pnt = Point(lng, lat)
        sqs = SearchQuerySet().using('mobile_api').filter(django_ct='core.coupon', online=False,
                                                          is_duplicate=False, is_deleted=False, status='considered-active')\
                                                .exclude(end__lt=datetime.now(pytz.utc))\
                                                .dwithin('merchant_location', user_pnt, radius).distance('merchant_location', user_pnt)\
                                                .order_by('distance')

        if 'query' in params_keys:
            query = params_dict['query']
            sqs_by_query = SearchQuerySet().using('mobile_api').filter(mobilequery=query)
            sqs = sqs.__and__(sqs_by_query)

            # Prepare for 'localindex' api service
            self.create_localinfo_index_if_doesnt_exist()
            matched_category_indices = [i for i, s in enumerate(self.available_categories_list) if query.lower() in s.lower()]
            matched_category_names = [self.available_categories_list[i] for i in matched_category_indices]
            self.index_it_in_localinfo_populars(id_param, location_param, string.capwords(query), matched_category_names)

        if 'category_slugs' in params_keys:
            category_slugs_list = params_dict['category_slugs'].split(',')
            sqs_by_category = SearchQuerySet().using('mobile_api')
            for c in category_slugs_list:
                sqs_by_category = sqs_by_category.filter_or(category_slugs=c.strip())
            sqs = sqs.__and__(sqs_by_category)

        if 'provider_slugs' in params_keys:
            provider_slugs_list = params_dict['provider_slugs'].split(',')
            sqs_by_provider = SearchQuerySet().using('mobile_api')
            for p in provider_slugs_list:
                sqs_by_provider = sqs_by_provider.filter_or(provider_slugs=p.strip())
            sqs = sqs.__and__(sqs_by_provider)

        updated_after = params_dict.get('updated_after', None)
        per_page = int(params_dict.get('per_page', 20))
        page = int(params_dict.get('page', 1))
        start_point = (page - 1) * per_page
        end_point = page * per_page

        deals = []

        for sqs_obj in sqs[start_point:end_point]:
            merchant_pnt = sqs_obj.merchant_location
            if not merchant_pnt:
                continue
            dist_to_user = geopy_distance((user_pnt.y, user_pnt.x), (merchant_pnt.y, merchant_pnt.x)).miles

            deal_description = sqs_obj.text
            if sqs_obj.related_deals_count != 0:
                deal_description = deal_description if deal_description else ""
                deal_description += "\n\nFind {} more similar deal(s) from this vendor on {}!".format(sqs_obj.related_deals_count,
                                                                                                      sqs_obj.provider)
            each_deal = {'deal':
                {
                    'id':                   sqs_obj.coupon_ref_id,
                    'title':                sqs_obj.embedly_title,
                    'short_title':          sqs_obj.embedly_description,
                    'description':          deal_description,
                    'fine_print':           sqs_obj.restrictions,
                    'number_sold':          None,
                    'url':                  sqs_obj.link,
                    'untracked_url':        sqs_obj.directlink,
                    'price':                sqs_obj.price,
                    'value':                sqs_obj.listprice,
                    'discount_amount':      sqs_obj.discount,
                    'discount_percentage':  float(sqs_obj.percent) / 100,
                    'commission':           None,
                    'provider_name':        sqs_obj.provider,
                    'provider_slug':        sqs_obj.provider_slug,
                    'category_name':        ', '.join(sqs_obj.categories) if sqs_obj.categories else None,
                    'category_slug':        ', '.join(sqs_obj.category_slugs) if sqs_obj.category_slugs else None,
                    'image_url':            sqs_obj.image,
                    'online':               sqs_obj.online,
                    'expires_at':           sqs_obj.end,
                    'created_at':           sqs_obj.start,
                    'updated_at':           sqs_obj.lastupdated,
                    'is_duplicate':         sqs_obj.is_duplicate,
                    'merchant': {
                        'id':               sqs_obj.merchant_ref_id,
                        'name':             sqs_obj.merchant_name,
                        'address':          sqs_obj.merchant_address,
                        'locality':         sqs_obj.merchant_locality,
                        'region':           sqs_obj.merchant_region,
                        'postal_code':      sqs_obj.merchant_postal_code,
                        'country':          "United States",
                        'country_code':     "US",
                        'latitude':         merchant_pnt.y,
                        'longitude':        merchant_pnt.x,
                        'dist_to_user_mi':  dist_to_user,
                        'url':              sqs_obj.merchant_link,
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


    def single_deal_return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        params_dict = request.GET
        ref_id_param = params_dict.get('ref_id', None)
        if not ref_id_param:
            response = {
                'deal': {},
                'res_status': {
                    'error': True,
                    'message': 'You must supply a reference id of a coupon you are looking for.',
                }
            }
            return self.create_response(request, response)

        sqs = SearchQuerySet().using('mobile_api').filter(django_ct='core.coupon', coupon_ref_id=ref_id_param)

        if not sqs.count():
            deal_data     = {}
            error_boolean = True
            res_message   = "Unable to retrieve a deal with this ref_id: {}".format(ref_id_param)
        else:
            sqs_obj = sqs[0]
            merchant_pnt = sqs_obj.merchant_location
            if not merchant_pnt:
                deal_data = {}
                error_boolean = True
                res_message   = "Requested deal has no redeemable location(s) available."
            else:
                deal_description = sqs_obj.text
                if sqs_obj.related_deals_count != 0:
                    deal_description = deal_description if deal_description else ""
                    deal_description += "\n\nFind {} more similar deal(s) from this vendor on {}!".format(sqs_obj.related_deals_count,
                                                                                                          sqs_obj.provider)
                deal_data     = {
                    'id':                   sqs_obj.coupon_ref_id,
                    'title':                sqs_obj.embedly_title,
                    'short_title':          sqs_obj.embedly_description,
                    'description':          deal_description,
                    'fine_print':           sqs_obj.restrictions,
                    'number_sold':          None,
                    'url':                  sqs_obj.link,
                    'untracked_url':        sqs_obj.directlink,
                    'price':                sqs_obj.price,
                    'value':                sqs_obj.listprice,
                    'discount_amount':      sqs_obj.discount,
                    'discount_percentage':  float(sqs_obj.percent) / 100,
                    'commission':           None,
                    'provider_name':        sqs_obj.provider,
                    'provider_slug':        sqs_obj.provider_slug,
                    'category_name':        ', '.join(sqs_obj.categories) if sqs_obj.categories else None,
                    'category_slug':        ', '.join(sqs_obj.category_slugs) if sqs_obj.category_slugs else None,
                    'image_url':            sqs_obj.image,
                    'online':               sqs_obj.online,
                    'expires_at':           sqs_obj.end,
                    'created_at':           sqs_obj.start,
                    'updated_at':           sqs_obj.lastupdated,
                    'is_duplicate':         sqs_obj.is_duplicate,
                    'merchant': {
                        'id':               sqs_obj.merchant_ref_id,
                        'name':             sqs_obj.merchant_name,
                        'address':          sqs_obj.merchant_address,
                        'locality':         sqs_obj.merchant_locality,
                        'region':           sqs_obj.merchant_region,
                        'postal_code':      sqs_obj.merchant_postal_code,
                        'country':          "United States",
                        'country_code':     "US",
                        'latitude':         merchant_pnt.y,
                        'longitude':        merchant_pnt.x,
                        'url':              sqs_obj.merchant_link,
                    }
                }
                error_boolean = False
                res_message   = "Successfully retrieved the requested deal."

        response = {
            'deal': deal_data,
            'res_status': {
                'error': error_boolean,
                'message': res_message,
            }
        }
        return self.create_response(request, response)


    def localinfo_return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.create_localinfo_index_if_doesnt_exist()

        params_dict = request.GET
        params_keys = params_dict.keys()
        try:
            location_param = params_dict['location']
        except:
            response = {
                'error': {'message': "You must supply a valid user location information."}
            }
            return self.create_response(request, response)
        lat_lng_in_list = location_param.split(',')
        lat, lng = map(float, lat_lng_in_list)
        user_pnt = Point(lng, lat)
        radius = D(mi=float(params_dict['radius'])) if 'radius' in params_keys else D(mi=100)

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

        res = self.es.search(index="localinfo", doc_type='populars', body=filters)
        popular_nearby_list_raw = res['facets']['search_keyword']['terms']
        # popular_category_list_raw = res['facets']['search_category']['terms'] # Not used for now; instead of parent categories.

        default_image = self.find_default_image(user_pnt)
        base_response = {
            "default_image": default_image,
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

        # Always show parent categories as 'popular categories' (minus Special Interest and Product )
        for c in self.parent_categories_list:
            popular_category = self.return_popular_something_insert(user_pnt, c)
            popular_category_sub_structure['list'].append(popular_category)
        base_response['search_categories'].append(popular_category_sub_structure)

        # Always try to show 5 'popular nearby's based on historical searches (min occurance threshold at 100);
        # To the extent there aren't enough historical popular nearbys, then fill the rest with
        # randomly selected categories, provided that there are at least 10 deals available under each category.
        # The user's location & poular_nearbys pair is cached and used for 12hrs; If the user's location changes
        # more than 50 miles away from any cached locations, then generate a new list of popular nearbys.
        id_param = params_dict.get('id', 'uuid')
        cached_data = cache.get(id_param) if id_param != 'uuid' else None

        if cached_data:
            cached_locations = cached_data['pop_nearbys'].keys()
            closest_pnt_to_user = {}
            for location in cached_locations:
                lat, lng = map(float, location.split(','))
                dist_to_user = geopy_distance((user_pnt.y, user_pnt.x), (lat, lng)).miles
                if len(closest_pnt_to_user) == 0:
                    closest_pnt_to_user = {location: dist_to_user}
                    continue

                closest_dist_so_far = closest_pnt_to_user.values()[0]
                if dist_to_user < closest_dist_so_far:
                    closest_pnt_to_user = {location: dist_to_user}
                else:
                    continue

        max_dist_for_caching = 50 # miles
        if cached_data and (closest_pnt_to_user.values()[0] <= max_dist_for_caching):
            closest_lat_lng = closest_pnt_to_user.keys()[0]
            cached_popular_nearbys = cached_data['pop_nearbys'][closest_lat_lng]
            for n in cached_popular_nearbys:
                popular_nearby = self.return_popular_something_insert(user_pnt, n)
                popular_nearby_sub_structure['list'].append(popular_nearby)
            base_response['search_categories'].append(popular_nearby_sub_structure)
        else:
            max_nearbys = 5
            for kw in popular_nearby_list_raw[:max_nearbys]:
                if kw['count'] < 100:
                    break
                else:
                    popular_nearby = self.return_popular_something_insert(user_pnt, kw['term'])
                    popular_nearby_sub_structure['list'].append(popular_nearby)

            categories_to_sample_from = copy.copy(self.sanitized_categories_list)
            while True:
                popular_nearbys_so_far = [n['name'] for n in popular_nearby_sub_structure['list']]
                if len(popular_nearbys_so_far) >= max_nearbys:
                    break

                try:
                    random_pick = random.sample(categories_to_sample_from, 1)[0]
                except ValueError: # When ran out of categories to choose from.
                    break

                sqs = SearchQuerySet().using('mobile_api')\
                                      .filter(django_ct='core.coupon', online=False, is_duplicate=False,
                                              is_deleted=False, status='considered-active', mobilequery=random_pick)\
                                      .exclude(end__lt=datetime.now(pytz.utc))\
                                      .dwithin('merchant_location', user_pnt, radius)\
                                      .distance('merchant_location', user_pnt).order_by('distance')
                if (random_pick in popular_nearbys_so_far) or (len(sqs) < 10):
                    categories_to_sample_from.remove(random_pick)
                    continue
                else:
                    popular_nearby = self.return_popular_something_insert(user_pnt, random_pick)
                    popular_nearby_sub_structure['list'].append(popular_nearby)
                    categories_to_sample_from.remove(random_pick)
            popular_nearbys_so_far = [n['name'] for n in popular_nearby_sub_structure['list']]
            if popular_nearbys_so_far:
                base_response['search_categories'].append(popular_nearby_sub_structure)
                if id_param != 'uuid':
                    self.cache_it_with_location(id_param, popular_nearbys_so_far, location_param)

        # only for debugging purposes below
        # base_response['elasticsearch_res'] = res

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

        # Exclude parent categories that are already being presented as 'popular categories'
        categories_to_exclude_list += self.parent_categories_list

        if category in categories_to_exclude_list:
            return False
        return True

    def return_popular_something_insert(self, user_pnt, category_or_keyword):
        picture_url = None
        # cities = SearchQuerySet().using('mobile_api').filter(django_ct='core.citypicture')\
        #                          .distance('geometry', user_pnt).order_by('distance')
        # closest_city = cities[0]
        # if (category_or_keyword == 'Health & Beauty') and (closest_city.text == 'Albuquerque, NM'):
        #     picture_url = 'https://s3.amazonaws.com/pushpennyapp/health-beauty.jpg'

        popular_something = {
            "image": picture_url,
            "name": category_or_keyword
        }
        return popular_something

    def cache_it_with_location(self, uuid, popular_nearbys_list, lat_lng_str):
        cached_data = cache.get(uuid)

        if cached_data:
            location_popular_pairs = cached_data['pop_nearbys']
            location_popular_pairs[lat_lng_str] = popular_nearbys_list
        else:
            location_popular_pairs = {lat_lng_str: popular_nearbys_list}
        cache.set(uuid, {'pop_nearbys': location_popular_pairs}, 60 * 60 * 12) # Cache it for 12 hours

    def find_default_image(self, user_pnt):
        cities = SearchQuerySet().using('mobile_api').filter(django_ct='core.citypicture')\
                                 .distance('geometry', user_pnt).order_by('distance')
        closest_city = cities[0]
        dist_btwn_city_user = geopy_distance((user_pnt.y, user_pnt.x), (closest_city.geometry.y, closest_city.geometry.x)).miles
        if dist_btwn_city_user <= closest_city.radius:
            default_image = closest_city.picture_url
        else:
            try:
                default = cities.filter(text='Default')[0]
                default_image = default.picture_url
            except:
                default_image = 'https://s3.amazonaws.com/pushpennyapp/pushpenny-default.jpg'
        return default_image
