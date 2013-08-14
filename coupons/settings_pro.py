from settings import *

HostName = 'pennywyse.com'
BASE_URL_NO_APPENDED_SLASH = 'http://' + HostName
SVCS_HOST = HostName

ALLOWED_HOSTS = ['pennywyse.com', 'www.pennywyse.com']

STATIC_URL = '//d1094zu9qp7ilj.cloudfront.net/'
STATICFILES_STORAGE = 'coupons.storage.S3PipelineStorage'
