from basesettings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ["pushpenny.com","www.pushpenny.com"]

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

