from settings import *

HostName = 'pennywyse.herokuapp.com'
BASE_URL_NO_APPENDED_SLASH = 'http://' + HostName
SVCS_HOST = HostName

ALLOWED_HOSTS = [HostName, '127.0.0.1', 'localhost']

DEBUG = False
TEMPLATE_DEBUG = DEBUG

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG['SHOW_TOOLBAR_CALLBACK'] = show_toolbar

#STATIC_URL = 'http://d2nixvjj44pjq8.cloudfront.net/static/'

#SECRET_KEY = 'VtkbsjjstNxTCQTYopimAj5c3lbMdQHHCBShyCCxosCntEyzuk'