from settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['pennywyse.com', 'www.pennywyse.com']

HostName = 'pennywyse.com'
BASE_URL_NO_APPENDED_SLASH = 'http://' + HostName
SVCS_HOST = HostName

#STATIC_URL = 'http://d2nixvjj44pjq8.cloudfront.net/static/'