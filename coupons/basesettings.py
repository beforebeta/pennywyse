import os, datetime

__author__ = 'amrish'

FMTC_ACCESS_KEY = '43a787c3f5f2cf2f675cbf86aff6a33b'

BASE_DIR = "/Users/asingh/Dropbox/workspace/coupons/"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

IMAGE_LOCAL_COPY_DIR_NO_PREFIX = 'static/img/local/'
IMAGE_LOCAL_COPY_DIR = 'static/img/local/'

BASE_URL_NO_APPENDED_SLASH = "http://localhost:8002"
try: os.makedirs(IMAGE_LOCAL_COPY_DIR)
except: pass

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

WEBSITE_NAME = 'PennyWyse'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'coupons',                      # Or path to database file if using sqlite3.
        'USER': 'dbuser',                      # Not used with sqlite3.
        'PASSWORD': 'dbuser',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '8001',                      # Set to empty string for default. Not used with sqlite3.
        'DEFAULT_STORAGE_ENGINE': 'MyISAM'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    "./static/",
    )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
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
    "web.context_processors.base",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
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
    'tracking.middleware.VisitorTrackingMiddleware',
    'tracking.middleware.BannedIPMiddleware'
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

ROOT_URLCONF = 'coupons.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'coupons.wsgi.application'

TEMPLATE_DIRS = (
    'templates/',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
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
    'tracking',
    'articles',
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

DEFAULT_IMAGE = "http://pennywyse.com/static/img/favicon.png"

APP_NAME = "COUPONS_APP"
APPEND_SLASH=True

########################################################################
# Tracking

#Skimlinks Reporting API Keys'
SKIMLINKS_REPORTING_PRIVATE_KEY = "e7d0c5228bbf4ca56864188e780b2b6d"
SKIMLINKS_REPORTING_PUBLIC_KEY = "067eada877c2bbc1698a04bdc0c19c0a"

################
#   WEBSVCS
################

SVCS_SECRET_KEY = "a59bbf62-d332-471b-b8d3-494a97065fa1"

DEVELOPER_KEY = "00a1be63fcdf4cc39b9fa1c4c9e021ed990814ac740758b6eae34a9f71c27e8352950d4c5e37628f33690375a200ded9ffb2bcbe93e1f13a0525ea77c6fe52a719/4ac6543f61948191feb8b0db8b6ce4052d813140eaec8e9404c448f634ae7c530005b86783dad215c136a0f4fdf4ecf8d27390fda73847e7fba5c512b1b72849"

######################
# django-articles
######################
DISQUS_USER_API_KEY = "xEJVgJlNeCV3gcCD9w5b67kP8QaZi2R51JCaQuycadblRxI29ADap9MC9EViXEzq"
DISQUS_FORUM_SHORTNAME = "pennywyse"
ARTICLES_AUTO_TAG = False
ARTICLE_PAGINATION = 10

#S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'coupons.storage.S3PipelineStorage'

AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = False
AWS_REDUCED_REDUNDANCY = True
AWS_STORAGE_BUCKET_NAME = 'pennywyse'
AWS_HEADERS = {
    'Cache-Control': 'max-age=31556926',
    'Expires': (datetime.datetime.today() + datetime.timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
}
AWS_ACCESS_KEY_ID = 'AKIAISPVNQL76YJWH4WQ'
AWS_SECRET_ACCESS_KEY = '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'

#Embedly
EMBEDLY_KEY = "5918594fbe75489ea6f24784a3fff75d"
DOWNLOADER_CACHE_LOCATION = 'tmp/embedly'
