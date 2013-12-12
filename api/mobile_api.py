from tastypie.resources import ModelResource
# from geopy import geocoders
from geopy.distance import distance as geopy_distance
from haystack.query import SearchQuerySet
from haystack.utils.geo import Point, D

from core.models import Coupon

class DealsResource(ModelResource):
    class Meta:
        # queryset = Coupon.all_objects.filter(ref_id_source='sqoot')
        queryset = Coupon.objects.filter(ref_id_source='sqoot')
        resource_name = 'deals'

    def return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        # g = geocoders.GoogleV3()
        params_dict = request.GET
        params_keys = params_dict.keys()

        try:
            location_param = params_dict['location']
            lat_lng_in_list = location_param.split(',')
            lat = float(lat_lng_in_list[0])
            lng = float(lat_lng_in_list[1])
            # location, (lat, lng) = g.geocode(location_param)
        except:
            response = {
                'error': {'message': "You must supply a valid user location information."}
            }
            return self.create_response(request, response)

        '''
        # Check: sqs ordering based on proximity to user
        # NEED UPDATED_AFTER
        '''
        radius = D(mi=float(params_dict['radius'])) if 'radius' in params_keys else D(mi=10)
        user_pnt = Point(lng, lat)
        sqs = SearchQuerySet().filter(django_ct='core.coupon', coupon_source='sqoot', online=False, is_duplicate=False).dwithin('merchant_location', user_pnt, radius).distance('merchant_location', user_pnt).order_by('distance')

        if 'query' in params_keys:
            query = params_dict['query']
            sqs_by_query = SearchQuerySet().filter(mobilequery=query)
            sqs = sqs.__and__(sqs_by_query)

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
            if len(related_coupons) is not 0:
                deal_description = deal_description if coupon.description else ""
                deal_description += "\nFind More Deals From This Vendor on {}:\n".format(coupon_network.name)
                for c in related_coupons[:5]:
                    deal_description += c.embedly_title + "\n"

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
            'radius':                   float(params_dict['radius']),
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
