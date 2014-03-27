import base64
import json
from multiprocessing import Pool
import os.path
import re
import sys
from tempfile import NamedTemporaryFile
import time
import traceback
import urllib
from urlparse import urlparse, parse_qs

from BeautifulSoup import BeautifulSoup
import requests

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.contrib.gis import admin
from django.http import HttpResponse

from tracking.utils import get_visitor_tag

S3_BASE_URL = 'http://pushpenny.s3.amazonaws.com'

def extract_url_from_skimlinks(url):
    parsed_link = urlparse(url)
    if str(parsed_link.netloc) == 'go.redirectingat.com':
        qs = parse_qs(parsed_link.query)
        link = qs.get('url')
        if link:
            return link[0]
    return url

def url2path(url):
    return base64.urlsafe_b64encode(url)

def path2url(path):
    return base64.urlsafe_b64decode(path)

def encode_uri(uri):
    return urllib.quote(uri.encode("utf-8"), safe='~@#$&()*!+=:;,.?/\'')

def encode_uri_component(uri):
    return urllib.quote(uri.encode("utf-8"), safe='~()*!.\'')

def print_stack_trace():
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60

def get_first_google_image_result(query_string):
    return settings.DEFAULT_IMAGE

def get_description_tag_from_url(url):
    url = extract_url_from_skimlinks(url)
    data = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).content
    soup = BeautifulSoup(data)
    description = ""
    title = ""

    try:
        description = soup.head.find("meta",{"name":"description"})["content"]
    except:
        pass
    try:
        title = soup.head.title.text
    except:
        pass

    return description if description else title if title else url


def adaptive_cache_page(*dargs, **dkargs):
    def _decorator(f):
        def wrapper(request, *args, **kwargs):
            if request.is_ajax():
                return f(request, *args, **kwargs)
            cache_key = '_'.join(['%s:%s' % (k, w) for k,w in kwargs.items()])
            cached_response = cache.get(cache_key, '')
            if cached_response:
                if dkargs.get('assign_visitor_tag', True):
                    cached_response = replace_visitor_tag(cached_response, request.session['visitor_id'])
                return HttpResponse(cached_response, content_type='text/html; charset=utf-8')
            r = f(request, *args, **kwargs)
            if r.status_code == 200:
                data = r.content
                if dkargs.get('assign_visitor_tag', True):
                    data = replace_visitor_tag(data, request.session['visitor_id'])
                cache.set(cache_key, data, 60 * 60 * 24)
                return HttpResponse(data, content_type='text/html; charset=utf-8')
            return r
        return wrapper
    if len(dargs) == 1 and callable(dargs[0]):
        return _decorator(dargs[0])
    else:
        return _decorator


class CustomPaginator(Paginator):
    
    def __init__(self, *args, **kwargs):
        self.current_page = kwargs.pop('current_page', 1)
        return super(CustomPaginator, self).__init__(*args, **kwargs)
    
    @property
    def separators(self):
        separators = 0
        if self.num_pages > 12:
            if self.page <= 5 or self.current_page >= self.num_pages - 3:
                separators = 1
            separators = 2
        return separators
    
    @property
    def separated_pages(self):
        ppages = range(1, self.num_pages+1)
        if self.num_pages > 12:
            if self.page <= 5 or self.current_page >= self.num_pages - 3:
                ppages = ppages[:8] + ppages[-3:]
            else:
                page_next = self.current_page + 2
                page_prev = self.current_page - 2
                ppages = ppages[:3] + ppages[page_prev:page_next] + ppages[-3:]
        return ppages


def handle_exceptions(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyboardInterrupt as e:
            raise e
        except:
            print_stack_trace()
    return wrapper

def replace_visitor_tag(response, visitor_id):
    skimlinks = re.search('"#skimlinks.([.*]*[^"]+)"', response)
    if skimlinks:
        skimlinks_url = skimlinks.group(1)
        updated_skimlinks_url = get_visitor_tag(skimlinks_url, visitor_id)
        return response.replace(skimlinks.group(0), updated_skimlinks_url)
    return response


class CustomModelAdmin(admin.ModelAdmin):

    def save_model(self, *args, **kwargs):
        super(CustomModelAdmin, self).save_model(*args, **kwargs)
        cache.clear()
    
    def delete_model(self, *args, **kwargs):
        super(CustomModelAdmin, self).delete_model(*args, **kwargs)
        cache.clear()


def _upload_file(*args):
    from core.models import Coupon, Merchant
    try:
        model = args[0][0]
        ext = os.path.splitext(model.image)[1]
        dirname = 'coupons' if isinstance(model, Coupon) else 'merchants'
        filename = os.path.join('static/img/', dirname, str(model.id) + ext)
        if model.image:
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
                model.s3_image = os.path.join(S3_BASE_URL, filename)
            else:
                model.s3_image = os.path.join(S3_BASE_URL, 'static/img/favicon.png')
        else:
            model.s3_image = os.path.join(S3_BASE_URL, 'static/img/favicon.png')
        model.save()
    except Exception as e:
        print e

def upload_images_to_s3():
    from core.models import Coupon, Merchant
    for m in [Coupon, Merchant]:
        images =  list(m.objects.filter(s3_image__isnull=True)\
                                    .only('id', 'image', 's3_image'))
        tasks = Pool(50)
        tasks.map(_upload_file, zip(images))