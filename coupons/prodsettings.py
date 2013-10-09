from basesettings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ["pennywyse.com","www.pennywyse.com"]

BASE_DIR = "/root/public_html/pennywyse/"
BASE_URL_NO_APPENDED_SLASH = "http://pennywyse.com"
SVCS_HOST = "http://pennywyse.com"

#MEDIA_ROOT = '%sstatic/'% BASE_DIR
#MEDIA_URL = '/static/'

TEMPLATE_DIRS = (
    '%stemplates/' % BASE_DIR,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    )

IMAGE_LOCAL_COPY_DIR = '/root/public_html/pennywyse/static/img/local/'

try: os.makedirs(IMAGE_LOCAL_COPY_DIR)
except: pass

