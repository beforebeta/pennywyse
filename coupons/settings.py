# Django settings for coupons project.
import os
from basesettings import *

SVCS_HOST = "http://127.0.0.1:8000"

# for debug purposes
CELERY_ALWAYS_EAGER = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'web.utils.CustomSolrEngine',
        'URL': 'http://127.0.0.1:8080/solr',
        'EXCLUDED_INDEXES': ['web.search_indexes.LocalCouponIndex', 'web.search_indexes.CityPictureIndex']
    },
    'mobile_api': {
        'ENGINE': 'web.utils.CustomSolrEngine',
        'URL': 'http://127.0.0.1:8080/solr/mobile_api',
        'EXCLUDED_INDEXES': ['web.search_indexes.CouponIndex', 'web.search_indexes.MerchantIndex']
    },
}