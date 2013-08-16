from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

HostName = 'pennywyse.herokuapp.com'
BASE_URL_NO_APPENDED_SLASH = 'http://' + HostName
SVCS_HOST = HostName

ALLOWED_HOSTS = [HostName, '127.0.0.1', 'localhost']

# Static files

CDN = 'd1094zu9qp7ilj.cloudfront.net'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'coupons.storage.S3PipelineStorage'
STATIC_URL = '//' + CDN + '/'
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = STATIC_URL + MEDIA_DIR + '/'

# Debug toolbar

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG['SHOW_TOOLBAR_CALLBACK'] = show_toolbar
