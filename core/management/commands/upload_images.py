from multiprocessing import Pool
import os.path
from tempfile import NamedTemporaryFile
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from core.models import Coupon, Merchant
import requests

BASE_URL = 'http://pushpenny.s3.amazonaws.com'

class Command(BaseCommand):
    def handle(self, *args, **options):
        for m in [Coupon, Merchant]:
            images =  list(m.objects.filter(s3_image__isnull=True)\
                                        .exclude(image__isnull=True)\
                                        .only('id', 'image', 's3_image'))
            tasks = Pool(50)
            tasks.map(_upload_file, zip(images))
    
    
def _upload_file(*args):
    try:
        model = args[0][0]
        ext = os.path.splitext(model.image)[1]
        dirname = 'coupons' if isinstance(model, Coupon) else 'merchants'
        filename = os.path.join('static/img/', dirname, str(model.id) + ext)
        r = requests.get(model.image, stream=True)
        if r.status_code in [200, 301, 302]:
            f = NamedTemporaryFile(delete=False)
            for c in r.iter_content(chunk_size=2048):
                if c:
                    f.write(c)
                    f.flush()
            f.close()
            with open(f.name) as img:
                print 'Uploading %s' % filename
                default_storage.save(filename, File(img))
            os.unlink(f.name)
            model.s3_image = os.path.join(BASE_URL, filename)
        else:
            model.s3_image = os.path.join(BASE_URL, 'static/img/favicon.png')
        model.save()
    except Exception as e:
        print e