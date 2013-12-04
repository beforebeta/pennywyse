from tastypie.resources import ModelResource
from haystack.query import SearchQuerySet

from core.models import Coupon

class DealsResource(ModelResource):
    class Meta:
        queryset = Coupon.all_objects.filter(ref_id_source='sqoot')
        resource_name = 'deals'

    def return_response(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        # import ipdb; ipdb.set_trace()
        # request.GET.keys()
        # query = request.GET.get("q","") #.strip()
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
