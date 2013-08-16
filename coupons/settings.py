import os

import sys, urlparse
import datetime

#urlparse.uses_netloc.append('postgres')
urlparse.uses_netloc.append('mysql')

__author__ = 'amrish'

BASE_URL_NO_APPENDED_SLASH = ''

FMTC_ACCESS_KEY = '43a787c3f5f2cf2f675cbf86aff6a33b'

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(PROJECT_PATH, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

RAVEN_CONFIG = {
    'dsn': 'https://3068bc36ec7d4272ad85e90f19e57362:4d3431bd6ed241b382ace93a1b4a4050@app.getsentry.com/11687',
}

ADMINS = (
    ('Jacob Friis Saxberg', 'jacob@webcom.dk'),
)

MANAGERS = ADMINS

WEBSITE_NAME = 'PennyWyse'

if os.environ.has_key('DATABASE_URL'):
  url = urlparse.urlparse(os.environ['DATABASE_URL'])
  DATABASES = {
    'default': {
      'NAME':     url.path[1:],
      'USER':     url.username,
      'PASSWORD': url.password,
      'HOST':     url.hostname,
      'PORT':     url.port,
    }
  }
  if url.scheme == 'postgres':
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
  if url.scheme == 'mysql2':
    DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
    DATABASES['default']['DEFAULT_STORAGE_ENGINE'] = 'MyISAM'
else:
  # DATABASES = {
  #     'default': {
  #         'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
  #         'NAME': 'coupons',                      # Or path to database file if using sqlite3.
  #         'USER': 'dbuser',                      # Not used with sqlite3.
  #         'PASSWORD': 'dbuser',                  # Not used with sqlite3.
  #         'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
  #         'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
  #         'DEFAULT_STORAGE_ENGINE': 'MyISAM'
  #     }
  # }
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'penny.db')
    }
  }

#SOUTH_DATABASE_ADAPTERS = {'default':'django.db.backends.mysql'}
#SOUTH_DATABASE_ADAPTERS = {'default':'django.db.backends.sqlite3'}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

MEDIA_DIR = 'media'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: '/home/media/media.lawrence.com/media/'
MEDIA_ROOT = os.path.join(DATA_DIR, MEDIA_DIR)
# if not os.path.exists(MEDIA_ROOT):
#     os.makedirs(MEDIA_ROOT)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: 'http://media.lawrence.com/media/', 'http://example.com/media/'
MEDIA_URL = '/' + MEDIA_DIR + '/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' 'static/' subdirectories and in STATICFILES_DIRS.
# Example: '/home/media/media.lawrence.com/static/'
#STATIC_ROOT = '/static'
#STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir)) + '/static'
STATIC_ROOT = os.path.join(DATA_DIR, 'static')

# URL prefix for static files.
# Example: 'http://media.lawrence.com/static/'
#STATIC_URL = 'http://d2nixvjj44pjq8.cloudfront.net/'
#STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*-2y8lnpbs9h#$#2o21kr3u7rlld&amp;i+x+5wwsuy3wkmi6ig(9#'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'web.context_processors.base',
    'django.contrib.auth.context_processors.auth',
)

#PREPEND_WWW=True

MIDDLEWARE_CLASSES = (
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'web.middleware.WebMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'pipeline.middleware.MinifyHTMLMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    )

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

ROOT_URLCONF = 'coupons.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'coupons.wsgi.application'

TEMPLATE_DIRS = (
    'templates/',
    # Put strings here, like '/home/html/django_templates' or 'C:/www/django/templates'.
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'south',
    'core',
    'web',
    'websvcs',
    'ads',
    'raven.contrib.django.raven_compat',
    #'django_pdb',
    'debug_toolbar',
    'pipeline',
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}

DEFAULT_IMAGE = 'http://d1094zu9qp7ilj.cloudfront.net/img/favicon.png'

APP_NAME = 'COUPONS_APP'
APPEND_SLASH=True

################
#   WEBSVCS
################

SVCS_SECRET_KEY = 'a59bbf62-d332-471b-b8d3-494a97065fa1'

DEVELOPER_KEY = '00a1be63fcdf4cc39b9fa1c4c9e021ed990814ac740758b6eae34a9f71c27e8352950d4c5e37628f33690375a200ded9ffb2bcbe93e1f13a0525ea77c6fe52a719/4ac6543f61948191feb8b0db8b6ce4052d813140eaec8e9404c448f634ae7c530005b86783dad215c136a0f4fdf4ecf8d27390fda73847e7fba5c512b1b72849'

AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = False
AWS_REDUCED_REDUNDANCY = True
AWS_STORAGE_BUCKET_NAME = 'pennywyse'
AWS_HEADERS = {
    'Cache-Control': 'max-age=31556926',
    'Expires': (datetime.datetime.today() + datetime.timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
}


def get_cache():
  try:
    os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS'].replace(',', ';')
    os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
    os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
    return {
      'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'TIMEOUT': 24 * 60 * 60,
        'BINARY': True,
        'OPTIONS': { 'tcp_nodelay': True }
      }
    }
  except:
    return {
      'default': {
        #'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache'
      }
    }

CACHES = get_cache()
