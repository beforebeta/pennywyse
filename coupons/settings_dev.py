from settings import *

HostName = '127.0.0.1:8000'
BASE_URL_NO_APPENDED_SLASH = 'http://' + HostName
SVCS_HOST = HostName

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATIC_URL = '/static/'
