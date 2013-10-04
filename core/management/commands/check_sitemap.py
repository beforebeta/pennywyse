import sys
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
import requests
import grequests

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
                    self.urls.append(location.text)
                    # when number of URLs has reached SITEMAP_CHECK_LIMIT, making concurrent requests for those URLs
                    if len(self.urls) == settings.SITEMAP_CHECK_LIMIT:
                        self._check_urls()
            self._check_urls()
                    
        except Exception as e:
            self.stdout.write('Error: %s' % str(e))

    def _check_urls(self):
        """
        Concurrently checking bunch of URLs, limited by SITEMAP_CHECK_LIMIT setting,
        displaying progress in console.
        """
        
        r = (grequests.head(u) for u in self.urls)
        rs = grequests.map(r)
        self.error_urls += filter(lambda x: x.status_code not in [200, 301, 302], rs)
        self.checked_urls += len(self.urls)
        sys.stdout.write('\rChecked %s URLs, %s errors.' % (self.checked_urls, len(self.error_urls)))
        sys.stdout.flush()
        self.urls = []

    def handle(self, *args, **options):
        sys.stdout.write('\rChecking sitemaps.')
        self._check_sitemap(SITEMAP_URL)
        # if there any URLs that hasn't passed check - sending report by email to addresses, listed in SITEMAP_REPORT_RECIPIENTS
        if self.error_urls:
            report = '\n'.join(error_urls)
            email_message = EmailMessage('Sitemaps report', body='Report with list of URLs which returned error response codes is attached.', 
                                         from_email=settings.DEFAULT_FROM_EMAIL, to=settings.SITEMAP_REPORT_RECIPIENTS)
            email_message.attach('report.txt', report,'text/plain')
            email_message.send()
        else:
            sys.stdout.flush()
            sys.stdout.write('\rAll pages returned success response codes.')