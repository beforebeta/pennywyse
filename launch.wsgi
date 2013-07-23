import os
import sys
sys.path.append('/root/public_html/pennywyse/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'coupons.prodsettings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()