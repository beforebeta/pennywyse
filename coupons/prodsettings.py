from basesettings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ["pushpenny.com","www.pushpenny.com", "api.pushpenny.com"]

BASE_URL_NO_APPENDED_SLASH = "http://pushpenny.com"
SVCS_HOST = "http://pushpenny.com"

#MEDIA_ROOT = '%sstatic/'% BASE_DIR
#MEDIA_URL = '/static/'

TEMPLATE_DIRS = (
    abs_path('templates/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    )

IMAGE_LOCAL_COPY_DIR = abs_path('static/img/local/')

try: os.makedirs(IMAGE_LOCAL_COPY_DIR)
except: pass

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
        'URL': 'http://127.0.0.1:8080/solr',
        'EXCLUDED_INDEXES': ['web.search_indexes.LocalCouponIndex', 'web.search_indexes.CityPictureIndex']
    },
    'mobile_api': {
        'ENGINE': 'web.utils.CustomSolrEngine',
        'URL': 'http://127.0.0.1:8080/solr/mobile_api',
        'EXCLUDED_INDEXES': ['web.search_indexes.CouponIndex', 'web.search_indexes.MerchantIndex']
    },
}
