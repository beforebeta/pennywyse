from tastypie.resources import ModelResource
from geopy import geocoders
from haystack.query import SearchQuerySet, SQ
from haystack.utils.geo import Point, D

from core.models import Coupon

class DealsResource(ModelResource):
    class Meta:
        queryset = Coupon.all_objects.filter(ref_id_source='sqoot')
        resource_name = 'deals'

    def return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        g = geocoders.GoogleV3()
        params_dict = request.GET
        params_keys = params_dict.keys()

        try:
            location_param = params_dict['location']
            user_location, (lat, lng) = g.geocode(location_param)
        except:
            response = {
                'error': {'message': "You must supply a valid user location information."}
            }
            return self.create_response(request, response)

        # Retrieve all Sqoot local coupons
        sqs = SearchQuerySet().filter(django_ct='core.coupon', coupon_source='sqoot', online=False)

        # NEED TO ADD PROVIDER_SLUG & CATEGORY_SLUG FILTER & UPDATED_AFTER

        # Check the presense of 'query' param and execute/filter a full-text search ('OR' argument on all fields)
        if 'query' in params_keys:
            query = sqs.query.clean(params_dict['query'])
            sqs = sqs.filter(SQ(title=query) | SQ(content=query) | SQ(restrictions=query) | SQ(merchant_name=query) | SQ(categories=query))
            # sqs = sqs.filter_or(title=query, content=query, restrictions=query, merchant_name=query, categories=query)
            # sqs = sqs.filter_and(title=query, content=query, restrictions=query, merchant_name=query, categories=query)

        # Filter per location parameters AND re-order the query result based on proximity
        # REMINDER: Location filter must come last for ordering
        radius = D(mi=float(params_dict['radius'])) if 'radius' in params_keys else D(mi=10)
        pnt = Point(lng, lat)
        sqs = sqs.dwithin('merchant_location', pnt, radius).distance('merchant_location', pnt).order_by('distance')

        import ipdb; ipdb.set_trace()
        deals = []

        query = {
            'total': 999,
            'page': 999,
            'per_page': 999,
            'query': None,
            'location': None,
            'radius': 999,
            'online': None,
            'category_slugs': [],
            'provider_slugs': [],
            'updated_after': None,
        }

        each_deal = {
            'id': 1522115,
            'title': "Hair Straightening",
            'short_title': "40% off at MARIO At Design HairCut",
            'description': "<ul><li>Results last for months</li><li>Skilled and talented stylists</li><li>Straight hair with low maintenance</li><li>Straighten hair while keeping volume</li><li>Safe for highlights and color</li></ul>",
            'fine_print': None,
            'number_sold': None,
            'url': "http://api.sqoot.com/v2/deals/1522115/click?api_key=xhtihz",
            'untracked_url': "http://www.mytime.com/deals/CA/Santa-Monica/Health-&-Beauty/Hair-Straightening/MARIO-At-Design-HairCut/15518",
            'price': 150,
            'value': 250,
            'discount_amount': 100,
            'discount_percentage': 0.4,
            'commission': 7.5,
            'provider_name': "OfferSlot",
            'provider_slug': "offerslot",
            'category_name': "Health & Beauty",
            'category_slug': "health-beauty",
            'image_url': "https://api.sqoot.com/v2/deals/1522115/image?api_key=xhtihz",
            'online': False,
            'expires_at': None,
            'created_at': "2013-08-28T02:19:20Z",
            'updated_at': "2013-12-04T13:29:35Z",
            'merchant': {
                'id': 435407,
                'name': "MARIO At Design HairCut",
                'address': "7603 Santa Monica Blvd",
                'locality': "Los Angeles",
                'region': "CA",
                'postal_code': "90046",
                'country': "United States",
                'country_code': "US",
                'latitude': 34.09085,
                'longitude': -118.355079,
                'url': None
            }
        }

        deals.append(each_deal)

        response = {
            'query': query,
            'deals': deals,
        }
        return self.create_response(request, response)
