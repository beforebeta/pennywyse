import os

import sys, urlparse
import datetime

urlparse.uses_netloc.append('postgres')
urlparse.uses_netloc.append('mysql')

__author__ = 'amrish'

BASE_URL_NO_APPENDED_SLASH = ''

FMTC_ACCESS_KEY = '43a787c3f5f2cf2f675cbf86aff6a33b'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

RAVEN_CONFIG = {
    'dsn': 'https://3068bc36ec7d4272ad85e90f19e57362:4d3431bd6ed241b382ace93a1b4a4050@app.getsentry.com/11687',
}

IMAGE_LOCAL_COPY_DIR_NO_PREFIX = 'static/img/local/'
IMAGE_LOCAL_COPY_DIR = BASE_DIR + '/' + IMAGE_LOCAL_COPY_DIR_NO_PREFIX
if not os.path.exists(IMAGE_LOCAL_COPY_DIR):
    os.makedirs(IMAGE_LOCAL_COPY_DIR)

ADMINS = (
    ('Jacob Friis Saxberg', 'jacob@webcom.dk'),
)

WEBSITE_NAME = 'PennyWyse'

MANAGERS = ADMINS

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
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'GMT'

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
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: '/home/media/media.lawrence.com/media/'
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: 'http://media.lawrence.com/media/', 'http://example.com/media/'
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' 'static/' subdirectories and in STATICFILES_DIRS.
# Example: '/home/media/media.lawrence.com/static/'
#STATIC_ROOT = '/static'
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir)) + '/static'

# URL prefix for static files.
# Example: 'http://media.lawrence.com/static/'
#STATIC_URL = 'http://d2nixvjj44pjq8.cloudfront.net/'
#STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

#STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

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
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'web.middleware.WebMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'pipeline.middleware.MinifyHTMLMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

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
    #'south',
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

DEFAULT_IMAGE = 'http://pennywyse.com/static/img/favicon.png'

APP_NAME = 'COUPONS_APP'
APPEND_SLASH=True

################
#   WEBSVCS
################

SVCS_SECRET_KEY = 'a59bbf62-d332-471b-b8d3-494a97065fa1'

DEVELOPER_KEY = '00a1be63fcdf4cc39b9fa1c4c9e021ed990814ac740758b6eae34a9f71c27e8352950d4c5e37628f33690375a200ded9ffb2bcbe93e1f13a0525ea77c6fe52a719/4ac6543f61948191feb8b0db8b6ce4052d813140eaec8e9404c448f634ae7c530005b86783dad215c136a0f4fdf4ecf8d27390fda73847e7fba5c512b1b72849'

# import warnings
# warnings.filterwarnings('error', r'DateTimeField received a naive datetime', RuntimeWarning, r'django\.db\.models\.fields')

### Static ###
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#STATICFILES_STORAGE = 'coupons.storage.S3PipelineStorage'
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
AWS_STORAGE_BUCKET_NAME = 'pennywyse'
AWS_HEADERS = {
    'Cache-Control': 'max-age=31556926, public',
    'Expires': (datetime.datetime.today() + datetime.timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
}

if DEBUG:
    STATIC_URL = '/static/'
else:
    STATIC_URL = '//d1094zu9qp7ilj.cloudfront.net/'
