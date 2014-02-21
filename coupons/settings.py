# Django settings for coupons project.
import os
from basesettings import *

SVCS_HOST = "http://127.0.0.1:8000"

# for debug purposes
CELERY_ALWAYS_EAGER = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'web.utils.CustomSolrEngine',
        'URL': 'http://192.241.162.96:8080/solr',
        'EXCLUDED_INDEXES': ['web.search_indexes.LocalCouponIndex', 'web.search_indexes.CityPictureIndex']
    },
    'mobile_api': {
        'ENGINE': 'web.utils.CustomSolrEngine',
        'URL': 'http://192.241.162.96:8080/solr/mobile_api',
        'EXCLUDED_INDEXES': ['web.search_indexes.CouponIndex', 'web.search_indexes.MerchantIndex']
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'coupons',
        'USER': 'pushpenny_mobile',
        'PASSWORD': 'bmp@V73_q^UT[F>^Z?,vj2zK',
        'HOST': '192.241.162.96',
        'DEFAULT_STORAGE_ENGINE': 'MyISAM',
        'OPTIONS': { 'init_command': 'SET storage_engine=MYISAM' },
    }
}

