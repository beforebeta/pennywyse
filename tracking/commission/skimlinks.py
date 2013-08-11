import hashlib
import datetime
from time import strftime
import urllib
from django.conf import settings
import requests

REPORTING_ENDPOINT = 'https://api-reports.skimlinks.com'

class ReportingAPI():

    def test(self):
        return _get_response('/publisher/test', {}).content

    def get_commissions(self):
        return _get_response('/publisher/reportcommissions', {
            'startDate'     : '2011-12-01',
            'endDate'       : datetime.date.today().isoformat()
        }).content

def _md5(message):
    return hashlib.md5(message).hexdigest()

def _get_timestamp():
    return strftime("%Y-%m-%dT%H:%M:%S+00:00")

def _get_quoted(components):
    return urllib.quote(components.encode("utf-8"))

def _create_auth_token():
    timestamp = _get_timestamp()
    return timestamp, _md5(timestamp + settings.SKIMLINKS_REPORTING_PRIVATE_KEY)

def _get_response(path, arguments):
    timestamp, token = _create_auth_token()
    arguments['timestamp']  = timestamp
    arguments['apikey']     = settings.SKIMLINKS_REPORTING_PUBLIC_KEY,
    arguments['authtoken']  = token,
    arguments['format']     = 'json'
    return requests.get(REPORTING_ENDPOINT + path, params=arguments)

