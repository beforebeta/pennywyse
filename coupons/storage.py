from django.contrib.staticfiles.storage import CachedFilesMixin
from pipeline.storage import PipelineMixin
from storages.backends.s3boto import S3BotoStorage

class S3PipelineStorage(PipelineMixin, CachedFilesMixin, S3BotoStorage):

    def __init__(self, *args, **kwargs):
        # todo: read from env or settings
        kwargs['bucket'] = 'pennywyse'
        kwargs['custom_domain'] = 'd1094zu9qp7ilj.cloudfront.net'
        super(S3PipelineStorage, self).__init__(*args, **kwargs)
