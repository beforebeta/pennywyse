from basesettings import *

base_dir = "/root/public_html/pennywyse/"

SVCS_HOST = "http://pennywyse.com"

#MEDIA_ROOT = '%sstatic/'% base_dir
#MEDIA_URL = '/static/'

TEMPLATE_DIRS = (
    '%stemplates/' % base_dir,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    )

IMAGE_LOCAL_COPY_DIR = '/root/public_html/pennywyse/static/img/local/'

try: os.makedirs(IMAGE_LOCAL_COPY_DIR)
except: pass
