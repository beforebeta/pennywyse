import json

import requests
from tastypie.resources import ModelResource

from core.models import Coupon

# from core.models import Coupon

class DealsResource(ModelResource):
    class Meta:
        queryset = Coupon.all_objects.filter(ref_id_source='sqoot')
        resource_name = 'deals'









# class dict2obj(object):
#     """
#     Convert dictionary to object
#     @source http://stackoverflow.com/a/1305561/383912
#     """
#     def __init__(self, d):
#         self.__dict__['d'] = d

#     def __getattr__(self, key):
#         value = self.__dict__['d'][key]
#         if type(value) == type({}):
#             return dict2obj(value)
#         return value


# class DealsResource(Resource):
#     #deals = fields.ListField(attribute='deal')
#     #deal = fields.DictField(attribute='deal')
#     title = fields.CharField(attribute='title')
#     content = fields.CharField(attribute='content')
#     author = fields.CharField(attribute='author_name')

#     class Meta:
#         resource_name = 'deals'

#     def obj_get_list(self, bundle, **kwargs):
#         api_root        = "http://api.sqoot.com/v2/"

#         api_key         = bundle.request.GET.get('api_key', None)
#         query           = bundle.request.GET.get('query', None)
#         location        = bundle.request.GET.get('location', None)
#         radius          = bundle.request.GET.get('radius', 10)
#         online          = 'false'
#         provider_slugs  = bundle.request.GET.get('provider_slugs', None)
#         updated_after   = bundle.request.GET.get('updated_after', None)
#         per_page        = 100
#         order           = bundle.request.GET.get('order', None)

#         request_parameters = {
#             'api_key': api_key,
#             'query': query,
#             'location': location,
#             'radius': radius,
#             'online': online,
#             'provider_slugs': provider_slugs,
#             'updated_after': updated_after,
#             'per_page': per_page,
#             'order': order,
#         }

#         # sqoot_response_json = requests.get(api_root + 'deals', params=request_parameters).json()
#         #one_deal = requests.get(api_root + 'deals', params=request_parameters).json()['deals'][0]
#         deals = requests.get(api_root + 'deals', params=request_parameters).json()['deals']
#         _deals = []
#         for deal in deals:
#             _deals.append(deal["deal"])
#         #one_deal = deals[0]
#         #print one_deal
#         #
#         ##one_deal = json.loads(one_deal)
#         ## deals = []q
#         ## sample_dict = {'untracked_url': 'http://www.yelp.com/deals/dinner-and-massage-atlanta', 'updated_at': '2013-11-14T18:00:53Z'}
#         #
#         ## deals.append(dict2obj(
#         ##     {
#         ##         'deal': one_merchant,
#         ##     }
#         ## ))
#         #
#         posts = []
#         posts.append(dict2obj(
#             {
#                 'title': 'Test Blog Title 1',
#                 'content': 'Blog Content',
#                 'author_name': 'User 1',
#             }
#         ))
#         #posts.append(
#         #    {
#         #        'title': 'Test Blog Title 1',
#         #        'content': 'Blog Content',
#         #        'author_name': 'User 1',
#         #    }
#         #)


#         #posts.append(
#         #    {
#         #        'deal': one_deal,
#         #    }
#         #)
#         #
#         ##pdb.set_trace()
#         #return one_deal
#         #print deals[0]
#         #print type(deals[0])
#         #return deals
#         #return _deals
#         return posts