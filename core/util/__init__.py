import base64
import json
import re
import sys
import time
import traceback
import urllib
from urlparse import urlparse, parse_qs

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponse
from BeautifulSoup import BeautifulSoup
import requests

from tracking.utils import get_visitor_tag

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
            cached_response = unicode(cache.get(cache_key, ''))
            if cached_response:
                if dkargs.get('assign_visitor_tag', True):
                    cached_response = replace_visitor_tag(cached_response, request.visitor.id)
                return HttpResponse(cached_response, content_type='text/html; charset=utf-8')
            r = f(request, *args, **kwargs).content
            if dkargs.get('assign_visitor_tag', True):
                r = replace_visitor_tag(r, request.visitor.id)
            cache.set(cache_key, r, 60 * 60 * 24)
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