# Django settings for coupons project.
import os, datetime
from basesettings import *

SVCS_HOST = "http://127.0.0.1:8000"
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
