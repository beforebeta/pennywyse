import sys
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
import requests
import grequests

from core.util import extract_url_from_skimlinks

SITEMAP_URL = 'http://s3.amazonaws.com/pennywyse/sitemap.xml'

class Command(BaseCommand):
    urls = []
    error_urls = []
    checked_urls = 0

    def _check_sitemap(self, url):
        """
        Fetching and parsing main sitemap, extracting sitemaps locations,
        then parsing them and preparing URLs for check.
        """
        
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text)
            for location in soup.findAll('loc'):
                if location.text.endswith('.xml'):
                    self._check_sitemap(location.text)
                else:
                    url = extract_url_from_skimlinks(location.text)
                    self.urls.append(url)
                    
        except Exception as e:
            sys.stdout.write('\nError: %s' % str(e))

    def _check_urls(self):
        """
        Concurrently checking bunch of URLs, limited by SITEMAP_CHECK_LIMIT setting,
        displaying progress in console.
        """
        
        total = len(self.urls)
        for i in range(0, len(self.urls), settings.SITEMAP_CHECK_LIMIT):
            r = (grequests.head(u) for u in self.urls[i:i+settings.SITEMAP_CHECK_LIMIT])
            rs = grequests.map(r)
            self.error_urls += filter(lambda x: x.status_code not in [200, 301, 302], rs)
            self.checked_urls += len(self.urls[i:i+settings.SITEMAP_CHECK_LIMIT])
            remained = total - self.checked_urls
            progress = round(self.checked_urls / total, 2)
            sys.stdout.write('\rChecked %.2f%% (%s URLs, %d errors, %d remained)' % (progress, self.checked_urls, 
                                                                             len(self.error_urls), remained))
            sys.stdout.flush()

    def handle(self, *args, **options):
        sys.stdout.write('\rChecking sitemaps.\n')
        sys.stdout.flush()
        self._check_sitemap(SITEMAP_URL)
        sys.stdout.write('\rChecking extracted URLs.\n')
        sys.stdout.flush()
        self._check_urls()
        # if there any URLs that hasn't passed check - sending report by email to addresses, listed in SITEMAP_REPORT_RECIPIENTS
        if self.error_urls:
            report = '\n'.join(error_urls)
            email_message = EmailMessage('Sitemaps report', body='Report with list of URLs which returned error response codes is attached.', 
                                         from_email=settings.DEFAULT_FROM_EMAIL, to=settings.SITEMAP_REPORT_RECIPIENTS)
            email_message.attach('report.txt', report,'text/plain')
            email_message.send()
        else:
            sys.stdout.write('\nAll pages returned success response codes.\n')