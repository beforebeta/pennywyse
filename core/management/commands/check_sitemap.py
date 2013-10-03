from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
import requests

SITEMAP_URL = 'http://s3.amazonaws.com/pennywyse/sitemap.xml'
TO_EMAIL = 'amrish@pennywyse.com'

class Command(BaseCommand):

    def _check_urls(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        for location in soup.findAll('loc'):
            if location.text.endswith('.xml'):
                self.stdout.write('Checking sitemap %s' % location.text)
                self._check_urls(location.text)
            else:
                self._check_url(location.text)

    def _check_url(self, url):
        r = requests.head(url)
        if r.status_code in [200, 301, 302]:
            self.stdout.write('%s OK' % url)
        else:
            self.stdout.write('%s ERROR' % url)
            return url


    def handle(self, *args, **options):
        self.stdout.write('Checking sitemaps.')
        error_urls = [u for u in self._check_urls(SITEMAP_URL)]
        if error_urls:
            report = '\n'.join(error_urls)
            email_message = EmailMessage('Sitemaps report', body='Report with list of URLs which returned error response codes is attached.', 
                                         from_email=settings.DEFAULT_FROM_EMAIL, to=[TO_EMAIL])
            email_message.attach('report.txt', report,'text/plain')
            email_message.send()
        else:
            self.stdout.write('All pages returned success response codes.')