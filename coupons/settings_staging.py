from settings import *

DEBUG = False
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

# Memcache

os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')

CACHES = {
  'default': {
    'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
    #'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
    'TIMEOUT': 500,
    'BINARY': True,
    'OPTIONS': { 'tcp_nodelay': True }
  }
}

# Debug toolbar

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG['SHOW_TOOLBAR_CALLBACK'] = show_toolbar
