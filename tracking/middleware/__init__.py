import logging

log = logging.getLogger('tracking.middleware')


# from datetime import datetime, timedelta
# import logging
# import re
# import traceback
#
# from django.conf import settings
# from django.contrib.auth.models import AnonymousUser
# from django.core.cache import cache
# from django.core.urlresolvers import reverse, NoReverseMatch
# from django.db.utils import DatabaseError
# from django.http import Http404
#
# from tracking import utils
# from tracking.models import Visitor, UntrackedUserAgent, BannedIP
# import pytz

# title_re = re.compile('<title>(.*?)</title>')

from cleanup import *
from visitor import *
from bannedip import *