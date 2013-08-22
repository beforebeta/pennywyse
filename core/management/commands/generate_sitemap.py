from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from core.models import Category
from core.models import Merchant
from core.models import Coupon
from subprocess import call
import datetime
import os

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.generate_category_urls()
        self.generate_merchant_urls()
        self.generate_coupon_urls()
        self.build_sitemaps()
        # self.gzip_sitemaps() # commented out because of trouble getting S3 tp serve gziped files
        self.build_sitemap_index()
        self.cleanup()

    def generate_category_urls(self):
        self.stdout.write('Generating Category URLs...')
        file = open('/tmp/pennywyse_sitemap_category_urls.txt', 'w')
        for category in Category.objects.all():
            file.write('http://pennywyse.com/categories/%s/ changefreq=weekly priority=0.7\n' % category.code)

            page_count = int((category.get_active_coupons.count() / 10.0) + 0.5)
            for i in range(1, page_count):
              file.write('http://pennywyse.com/categories/{0}/page/{1}/ changefreq=weekly priority=0.3\n'.format(category.code, i))
        file.close()

    def generate_merchant_urls(self):
        self.stdout.write('Generating Merchant URLs...')
        file = open('/tmp/pennywyse_sitemap_merchant_urls.txt', 'w')
        for merchant in Merchant.objects.all():
            file.write('http://pennywyse.com/coupons/{0}/{1}/ changefreq=weekly priority=0.7\n'.format(merchant.name_slug, merchant.id))
            file.write('http://pennywyse.com/coupons/{0}/ changefreq=weekly priority=0.7\n'.format(merchant.name_slug))

            page_count = int((merchant.get_active_coupons.count() / 10.0) + 0.5)
            for i in range(1, page_count):
              file.write('http://pennywyse.com/coupons/{0}/page/{1}/ changefreq=weekly priority=0.3\n'.format(merchant.name_slug, i))
              file.write('http://pennywyse.com/coupons/{0}/{1}/page/{2}/ changefreq=weekly priority=0.3\n'.format(merchant.name_slug, merchant.id, i))
        file.close()

    def generate_coupon_urls(self):
        self.stdout.write('Generating Coupon URLs...')
        file = open('/tmp/pennywyse_sitemap_coupon_urls.txt', 'w')
        for coupon in Coupon.objects.all():
            if coupon.merchant:
                file.write('http://pennywyse.com/coupon/{0}/{1}/{2}/ changefreq=weekly priority=0.7\n'.format(coupon.merchant.name_slug, coupon.desc_slug, coupon.id))
        file.close()

    def build_sitemaps(self):
        self.stdout.write('Building base sitemap...\n\n')
        call(['./vendor/sitemap_gen/sitemap_gen.py', '--config=sitemap/configs/base.xml'])
        self.stdout.write('Building category sitemap...\n\n')
        call(['./vendor/sitemap_gen/sitemap_gen.py', '--config=sitemap/configs/category.xml'])
        self.stdout.write('Building merchant sitemap...\n\n')
        call(['./vendor/sitemap_gen/sitemap_gen.py', '--config=sitemap/configs/merchant.xml'])
        self.stdout.write('Building coupon sitemap...\n\n')
        call(['./vendor/sitemap_gen/sitemap_gen.py', '--config=sitemap/configs/coupon.xml'])

    def gzip_sitemaps(self):
        self.stdout.write('gzipping...\n\n')

        call(['gzip', '-f', 'sitemap/base_sitemap.xml'])
        call(['gzip', '-f', 'sitemap/category_sitemap.xml'])
        call(['gzip', '-f', 'sitemap/coupon_sitemap.xml'])
        call(['gzip', '-f', 'sitemap/merchant_sitemap.xml'])


    def build_sitemap_index(self):
        self.stdout.write('Uploading sitemaps to S3...\n\n')
        base_url = default_storage.save('base_sitemap.xml', ContentFile(open('sitemap/base_sitemap.xml').read()))
        category_url = default_storage.save('category_sitemap.xml', ContentFile(open('sitemap/category_sitemap.xml').read()))
        coupon_url = default_storage.save('coupon_sitemap.xml', ContentFile(open('sitemap/coupon_sitemap.xml').read()))
        merchant_url = default_storage.save('merchant_sitemap.xml', ContentFile(open('sitemap/merchant_sitemap.xml').read()))
        last_updated = datetime.datetime.now().strftime('%Y-%m-%d')


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
  </sitemap>\n\
</sitemapindex>'.format(last_updated, 'http://s3.amazonaws.com/pennywyse/', base_url, category_url, coupon_url, merchant_url))
        file.close()

        self.stdout.write('Uploading the sitemap index to S3...\n\n')
        default_storage.save('sitemap.xml', ContentFile(open('sitemap/sitemap.xml').read()))

    def remove_sitemap(self, file_name):
        os.path.exists(file_name) and os.remove(file_name)
        os.path.exists(file_name + '.gz') and os.remove(file_name + '.gz')

    def cleanup(self):
        self.stdout.write('Cleaning up...\n\n')

        self.remove_sitemap('./sitemap/base_sitemap.xml')
        self.remove_sitemap('./sitemap/category_sitemap.xml')
        self.remove_sitemap('./sitemap/coupon_sitemap.xml')
        self.remove_sitemap('./sitemap/merchant_sitemap.xml')
        self.remove_sitemap('./sitemap/sitemap.xml')


        if Coupon.objects.count() > 50000:
            self.stdout.write('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n MORE THAN 50,000 COUPONS\nSplit Sitemap!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
