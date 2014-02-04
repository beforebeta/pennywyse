from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from core.models import Category
from core.models import Merchant
from core.models import Coupon
from subprocess import call
import datetime
import os
import requests
from lxml import etree
from core.management.commands.fmtcload import _download_content

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.cleanup()
        settings.AWS_DEFAULT_ACL = 'public-read'

        self.generate_category_urls()
        self.generate_merchant_urls()
        self.generate_blog_urls()
        self.build_sitemaps()
        # self.gzip_sitemaps() # commented out because of trouble getting S3 to serve gziped files
        self.build_sitemap_index()
        self.cleanup()

    def generate_category_urls(self):
        self.stdout.write('Generating Category URLs...')
        file = open('/tmp/pushpenny_sitemap_category_urls.txt', 'w')
        for category in Category.objects.all():
            file.write('http://pushpenny.com/categories/%s/ changefreq=weekly priority=0.7\n' % category.code)

            page_count = int((category.get_active_coupons().count() / 10.0) + 0.5)
            for i in range(1, page_count):
                file.write('http://pushpenny.com/categories/{0}/page/{1}/ changefreq=weekly priority=0.3\n'.format(category.code, i))
        file.close()

    def generate_merchant_urls(self):
        self.stdout.write('Generating Merchant URLs...')
        file = open('/tmp/pushpenny_sitemap_merchant_urls.txt', 'w')
        for merchant in Merchant.objects.all():
            file.write('http://pushpenny.com/coupons/{0}/ changefreq=weekly priority=0.7\n'.format(merchant.name_slug))

            page_count = int((merchant.get_active_coupons().count() / 10.0) + 0.5)
            for i in range(1, page_count):
                file.write('http://pushpenny.com/coupons/{0}/page/{1}/ changefreq=weekly priority=0.3\n'.format(merchant.name_slug, i))
        file.close()

    def generate_blog_urls(self):
        self.stdout.write('Generating Blog URLs...')
        f = open('/tmp/pushpenny_sitemap_blog_urls.txt', 'w')
        fh = _download_content('http://pushpenny.com/blog/feed/', '/tmp/blog_feed.txt')
        data = etree.iterparse(fh, tag='item')
        for event, item in data:
            link = item.find('link').text
            f.write('%s changefreq=weekly priority=0.7\n' % link)
        f.close()

    def chunks(self, l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]

    def build_sitemaps(self):
        for sitemap in ['base', 'category', 'merchant', 'blog']:
            self.stdout.write('Building %s sitemap...\n\n' % sitemap)
            call(['./vendor/sitemap_gen/sitemap_gen.py', '--config=sitemap/configs/%s.xml' % sitemap])

    def gzip_sitemaps(self):
        self.stdout.write('Archiving sitemaps...\n\n')

        call(['gzip', '-f', 'sitemap/base_sitemap.xml'])
        call(['gzip', '-f', 'sitemap/category_sitemap.xml'])
        call(['gzip', '-f', 'sitemap/merchant_sitemap.xml'])


    def build_sitemap_index(self):
        self.stdout.write('Uploading sitemaps to S3...\n\n')
        base_url = default_storage.save('base_sitemap.xml', ContentFile(open('sitemap/base_sitemap.xml').read()))
        category_url = default_storage.save('category_sitemap.xml', ContentFile(open('sitemap/category_sitemap.xml').read()))
        merchant_url = default_storage.save('merchant_sitemap.xml', ContentFile(open('sitemap/merchant_sitemap.xml').read()))
        blog_url = default_storage.save('blog_sitemap.xml', ContentFile(open('sitemap/blog_sitemap.xml').read()))

        last_updated = datetime.datetime.now().strftime('%Y-%m-%d')
        root = 'http://s3.amazonaws.com/pushpenny/'

        self.stdout.write('Updating the sitemap index...\n\n')
        file = open('sitemap/sitemap.xml', 'w')

        file.write('<?xml version="1.0" encoding="UTF-8"?>\n\
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\
  <sitemap>\n\
    <loc>{1}{2}</loc>\n\
    <lastmod>{0}</lastmod>\n\
  </sitemap>\n\
  <sitemap>\n\
    <loc>{1}{3}</loc>\n\
    <lastmod>{0}</lastmod>\n\
  </sitemap>\n\
  <sitemap>\n\
    <loc>{1}{4}</loc>\n\
    <lastmod>{0}</lastmod>\n\
  </sitemap>\n\
  <sitemap>\n\
    <loc>{1}{5}</loc>\n\
    <lastmod>{0}</lastmod>\n\
  </sitemap>\n'.format(last_updated, root, base_url, 
                       category_url, merchant_url, blog_url))

        file.write('</sitemapindex>')
        file.close()

        self.stdout.write('Uploading the sitemap index to S3...\n\n')
        default_storage.save('sitemap.xml', ContentFile(open('sitemap/sitemap.xml').read()))

    def remove_file(self, file_path):
        os.path.exists(file_path) and os.remove(file_path)

    def remove_sitemap(self, file_name):
        self.remove_file('./' + file_name)
        self.remove_file('./' + file_name + '.gz')
        self.remove_file('./sitemap/' + file_name)
        self.remove_file('./sitemap/' + file_name + '.gz')

    def cleanup(self):
        self.stdout.write('Cleaning up...\n\n')

        self.remove_sitemap('base_sitemap.xml')
        self.remove_sitemap('category_sitemap.xml')
        self.remove_sitemap('merchant_sitemap.xml')
        self.remove_sitemap('sitemap.xml')
