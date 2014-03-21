from basesettings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ["pushpenny.com","www.pushpenny.com", "api.pushpenny.com", "pushpennyapi.dfvops.com"]

BASE_URL_NO_APPENDED_SLASH = "http://pushpenny.com"
SVCS_HOST = "http://pushpenny.com"

ROOT_URLCONF = 'coupons.api_urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'pushpenny.log'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

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

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.gis',
    'compress',
    'djcelery',
    'haystack',
    'south',
    'api',
    'tastypie',
    'core',
    'web',
)

TEMPLATE_CONTEXT_PROCESSORS = ()

MIDDLEWARE_CLASSES = ()
