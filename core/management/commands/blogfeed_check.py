from django.utils.html import strip_tags
from django.core.management.base import BaseCommand

import requests
from BeautifulSoup import BeautifulSoup

PUSHPENNY_BLOG_URL = 'http://pushpenny.com/blog/feed/atom/'
# PUSHPENNY_BLOG_URL = 'http://pushpenny.com/blog/feed/'

class Command(BaseCommand):

    def handle(self, *args, **options):
        check_pushpenny_blog_feed()

def check_pushpenny_blog_feed():
    page = requests.get(PUSHPENNY_BLOG_URL)
    soup = BeautifulSoup(page.content)
    posts = soup.findAll('entry')

    print ''
    print 'INFO: Total of {} published posts'.format(len(posts))
    print ''
    print 'Title,Author,URL,Date Published,Word Count'

    for idx, p in enumerate(posts):
        title = p.find('title').text
        author = p.find('name').text
        link = p.find('link')['href'].split('?')[0]
        published_date = p.find('published').text
        clean_content = strip_tags(p.find('content').text)
        print "%s,%s,%s,%s,%s" % (title, author, link, published_date, len(clean_content.split(' ')))