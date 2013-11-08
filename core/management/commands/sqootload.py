import requests

from django.core.management.base import BaseCommand
from django.conf import settings

# from coupons.basesettings import SQOOT_PUBLIC_KEY

class Command(BaseCommand):

    def handle(self, *args, **options):
        # err = self.stderr
        # out = self.stdout
        print settings.SQOOT_PUBLIC_KEY


def scrape_sqoot():
    request_parameters = {
        # 'api_key': settings.SQOOT_PUBLIC_KEY,
        'api_key': SQOOT_PUBLIC_KEY,
        'per_page': 100,
        'page': 1,
    }
    # api_root = "http://api.sqoot.com/v2/"
    # all_deals = requests.get(api_root + 'deals', params=request_parameters)

    # all_deals.json().keys()
    # all_deals.json()


