from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from core.models import Category
from core.models import Merchant
from subprocess import call
import datetime
import os
from lxml import etree
from core.management.commands.fmtcload import _download_content

def generate_sitemap():
    _cleanup()
    settings.AWS_DEFAULT_ACL = 'public-read'

    _generate_category_urls()
    _generate_merchant_urls()
    _generate_blog_urls()
    _build_sitemaps()
    # _gzip_sitemaps() # commented out because of trouble getting S3 to serve gziped files
    _build_sitemap_index()
    _cleanup()


def _generate_category_urls():
    print 'Generating Category URLs...'
    file = open('/tmp/pushpenny_sitemap_category_urls.txt', 'w')
    for category in Category.objects.filter(ref_id_source__isnull=True):
        file.write('http://pushpenny.com/categories/%s/ changefreq=weekly priority=0.7\n' % category.code)

        page_count = int((category.get_active_coupons().count() / 20.0) + 0.5)
        for i in range(1, page_count):
            file.write('http://pushpenny.com/categories/{0}/page/{1}/ changefreq=weekly priority=0.3\n'.format(category.code, i))
    file.close()


def _generate_merchant_urls():
    print 'Generating Merchant URLs...'
    file = open('/tmp/pushpenny_sitemap_merchant_urls.txt', 'w')
    for merchant in Merchant.objects.all():
        file.write('http://pushpenny.com/coupons/{0}/ changefreq=weekly priority=0.7\n'.format(merchant.name_slug))

        page_count = int((merchant.get_active_coupons().count() / 20.0) + 0.5)
        for i in range(1, page_count):
            file.write('http://pushpenny.com/coupons/{0}/page/{1}/ changefreq=weekly priority=0.3\n'.format(merchant.name_slug, i))
    file.close()


def _generate_blog_urls():
    print 'Generating Blog URLs...'
    f = open('/tmp/pushpenny_sitemap_blog_urls.txt', 'w')
    fh = _download_content('http://pushpenny.com/blog/feed/', '/tmp/blog_feed.txt')
    data = etree.iterparse(fh, tag='item')
    for event, item in data:
        link = item.find('link').text
        f.write('%s changefreq=weekly priority=0.7\n' % link)
    f.close()


def _chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def _build_sitemaps():
    for sitemap in ['base', 'category', 'merchant', 'blog']:
        print 'Building %s sitemap...\n\n' % sitemap
        call(['./vendor/sitemap_gen/sitemap_gen.py', '--config=sitemap/configs/%s.xml' % sitemap])


def _gzip_sitemaps():
    print 'Archiving sitemaps...\n\n'
    call(['gzip', '-f', 'sitemap/base_sitemap.xml'])
    call(['gzip', '-f', 'sitemap/category_sitemap.xml'])
    call(['gzip', '-f', 'sitemap/merchant_sitemap.xml'])


def _build_sitemap_index():
    print 'Uploading sitemaps to S3...\n\n'
    base_url = default_storage.save('base_sitemap.xml', ContentFile(open('sitemap/base_sitemap.xml').read()))
    category_url = default_storage.save('category_sitemap.xml', ContentFile(open('sitemap/category_sitemap.xml').read()))
    merchant_url = default_storage.save('merchant_sitemap.xml', ContentFile(open('sitemap/merchant_sitemap.xml').read()))
    blog_url = default_storage.save('blog_sitemap.xml', ContentFile(open('sitemap/blog_sitemap.xml').read()))

    last_updated = datetime.datetime.now().strftime('%Y-%m-%d')
    root = 'http://s3.amazonaws.com/pushpenny/'

    print 'Updating the sitemap index...\n\n'
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

    print 'Uploading the sitemap index to S3...\n\n'
    default_storage.save('sitemap.xml', ContentFile(open('sitemap/sitemap.xml').read()))

def _remove_file(file_path):
    os.path.exists(file_path) and os.remove(file_path)


def _remove_sitemap(file_name):
    _remove_file('./' + file_name)
    _remove_file('./' + file_name + '.gz')
    _remove_file('./sitemap/' + file_name)
    _remove_file('./sitemap/' + file_name + '.gz')


def _cleanup():
    print 'Cleaning up...\n\n'
    _remove_sitemap('base_sitemap.xml')
    _remove_sitemap('category_sitemap.xml')
    _remove_sitemap('merchant_sitemap.xml')
    _remove_sitemap('sitemap.xml')