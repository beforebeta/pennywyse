from django.contrib.staticfiles.storage import CachedFilesMixin
from pipeline.storage import PipelineMixin
from storages.backends.s3boto import S3BotoStorage
from django.conf import settings
from core.util import print_stack_trace


class S3PipelineStorage(PipelineMixin, CachedFilesMixin, S3BotoStorage):

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.AWS_STORAGE_BUCKET_NAME
        # try:
        #     kwargs['custom_domain'] = settings.CDN
        # except:
        #     print_stack_trace()
        super(S3PipelineStorage, self).__init__(*args, **kwargs)
