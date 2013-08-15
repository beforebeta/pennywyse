from settings import *

HostName = 'pennywyse.com'
BASE_URL_NO_APPENDED_SLASH = 'http://' + HostName
SVCS_HOST = HostName

ALLOWED_HOSTS = ['pennywyse.com', 'www.pennywyse.com']

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'coupons.storage.S3PipelineStorage'
STATIC_URL = '//d1094zu9qp7ilj.cloudfront.net/'
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = STATIC_URL + MEDIA_DIR + '/'
