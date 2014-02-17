import base64
import json
import sys
import time
import traceback
import urllib
from urlparse import urlparse, parse_qs

from BeautifulSoup import BeautifulSoup
from django.conf import settings
import requests

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
#    print "$"*10, "Google Search for ", query_string
#    try:
#        #specific mappings
#        if query_string.lower() == "apparel":
#            return "http://apparelcyclopedia.com/wp-content/uploads/2013/04/american-apparel-clothing-fashion-store-sweaters-Favim.com-64206.jpg"
#        url = "https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + encode_uri_component(query_string.replace("-"," "))
#        j = json.loads(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).content)
#        return j["responseData"]["results"][0]["unescapedUrl"]
#    except:
#        print_stack_trace()
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


def handle_exceptions(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyboardInterrupt as e:
            raise e
        except:
            print_stack_trace()
    return wrapper
