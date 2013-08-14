from settings import *

HostName = 'pennywyse.herokuapp.com'
BASE_URL_NO_APPENDED_SLASH = 'http://' + HostName
SVCS_HOST = HostName

ALLOWED_HOSTS = [HostName, '127.0.0.1', 'localhost']

STATIC_URL = '//d1094zu9qp7ilj.cloudfront.net/'
STATICFILES_STORAGE = 'coupons.storage.S3PipelineStorage'

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG['SHOW_TOOLBAR_CALLBACK'] = show_toolbar
