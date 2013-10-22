import datetime
from optparse import make_option
import re
import string
import simplejson
import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand

import facebook
import requests
import twitter

from core.models import Coupon, Merchant
from web.models import PopularSocialCoupon

# list of facebook profiles to scrap posts from
FACEBOOK_SOURCES = ['EnzasBargains', 'TheKrazyCouponLady', 'smartcouponing101',
                   'couponingwithrachel', 'Hunt4Freebies.Coupons', 'couponmom']

# list of twitter accounts to scrap statuses from
TWITTER_SOURCES = ['SmartCouponing', 'CouponTweet']

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--get-facebook-coupons', action='store_true', dest='get_facebook_coupons', default=False),
        make_option('--get-twitter-coupons', action='store_true', dest='get_twitter_coupons', default=False)
    )
    
    merchant_names = '|'.join([m.name for m in Merchant.objects.all().only('name')])
    pattern = '(%s)[^\w|$]' % merchant_names    # regexp pattern for merchant recognition
    url_pattern = re.compile('((?:[a-z:\/]+)([a-zA-Z0-9_\+]+[.]{1}[a-zA-Z]{2,4})([^\s*]{0,}))', re.I)   # regexp pattern for URL recognition
    schema_pattern = re.compile('^(http|https)://', re.I)   # regexp pattern for URL schema recognition
    
    def _extract_full_url(self, url):
        """Expanding shortened URL."""
        
        # prepending URL schema if it does not have it, to avoid error
        if not re.search(self.schema_pattern, url):
            url = 'http://' + url
        try:
            r = requests.get(url)
            return r.url
        except Exception, e:
            print str(e)
        return url

    def _get_popularity(self, item_id):
        """Getting number of comments, shares and likes for facebook post, using FQL."""
        
        query = "SELECT comment_info, share_count, like_info FROM stream WHERE post_id='%s'"
        data = self.graph.fql(query=query % item_id)[0]
        popularity = data['like_info']['like_count'] + data['share_count'] + data['comment_info']['comment_count']
        return popularity
    
    def _parse_posts(self, path, until=None):
        """Iterating through list of posts, saving each post into DB, following pagination pages one by one."""
        
        args={'fields': 'id,message,updated_time,likes,comments,shares,link,type',
              'limit': '25'}
        if until:
            args.update(until=until)
        
        data = self.graph.request(path='/%s/posts' % path, args=args)
        for post in data['data']:
            url = short_url = ''
            message = post.get('message', None)
            if message:
                s = re.search(self.pattern, message, re.I)
                r = re.search(self.url_pattern, message)
                
                # determining coupon URL based on facebook post type
                if post['type'] == 'link':
                    short_url = post.get('link', None)
                    url = self._extract_full_url(short_url)
                elif r:
                    short_url = r.group(0)
                    url = self._extract_full_url(short_url)
                
                if s and PopularSocialCoupon.objects.filter(social_item_id=post['id']).count() == 0 and url:
                    merchant = Merchant.objects.filter(name=s.group(1))
                    if merchant:
                        popularity = self._get_popularity(post['id'])
                        message = message.replace(short_url, '')
                        c = PopularSocialCoupon.objects.create(merchant=merchant[0], ref_id='fb%s' % post['id'],
                                                               link=url, social_item_id=post['id'],
                                                               skimlinks=url, popularity=popularity,
                                                               social_source='http://facebook.com/%s' % path)
                        c.description = message
                        c.save()
                        print 'Imported facebook post %s' % post['id']
                else:
                    if not s:
                        print 'Ignored %s, merchant is not recognized' % post['id']
                    if not url:
                        print 'Ignored %s, no URL attached to facebook post' % post['id']
            else:
                print 'Ignored %s, message is not attached, post type %s' % (post['id'], post['type'])
        
        if data['data']:
            next_page = data['paging']['next']
            qs = urlparse.urlparse(next_page).query
            params = urlparse.parse_qs(qs)
            until = params['until'][0]
            # following next page in pagination
            self._parse_posts(path=path, until=until)
    
    def _parse_statuses(self, screen_name, since_id=None, max_id=None):
        params = {'screen_name': screen_name, 'count': 25}
        if since_id:
            params['since_id'] = since_id
        if max_id:
            params['max_id'] = max_id
        
        statuses = self.twitter_api.GetUserTimeline(**params)
        for status in statuses:
            s = re.search(self.pattern, status.text, re.I)
            if s and PopularSocialCoupon.objects.filter(social_item_id=status.id).count() == 0:
                if len(status.urls) > 0:
                    url = self._extract_full_url(status.urls[0].expanded_url)
                    popularity = status.retweet_count + status.favorite_count
                    merchant = Merchant.objects.filter(name=s.group(1))
                    text = status.text.replace(status.urls[0].url, '')
                    c = PopularSocialCoupon.objects.create(merchant=merchant[0], ref_id='tw%s' % status.id,
                                                           link=url, popularity=popularity, social_item_id=status.id,
                                                           skimlinks=url, social_source='http://twitter.com/%s' % screen_name)
                    c.description = text
                    c.save()
                    print 'Imported tweet %s' % status.id
                else:
                    print 'Ignored %s, no coupon link attached' % status.id
            else:
                print 'Ignored %s, merchant is not recognized' % status.id
        if statuses:
            ids = [s.id for s in statuses]
            if since_id:
                self._parse_statuses(screen_name, since_id=max(ids))
            if max_id or (not since_id and not max_id):
                self._parse_statuses(screen_name, max_id=min(ids))
            
        
    
    def handle(self, *args, **options):
        if options.get('get_facebook_coupons', None):
            access_token = facebook.get_app_access_token(settings.FACEBOOK_API_KEY, settings.FACEBOOK_API_SECRET)
            self.graph = facebook.GraphAPI(access_token)
            for path in FACEBOOK_SOURCES:   
                print 'Processing facebook account: %s' % path
                self._parse_posts(path)
        
        if options.get('get_twitter_coupons', None):
            self.twitter_api =  twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY, 
                               consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                               access_token_key=settings.TWITTER_ACCESS_TOKEN,
                               access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET)
            
            for screen_name in TWITTER_SOURCES:
                print 'Processing twitter timeline: %s' % screen_name
                #if PopularSocialCoupon.objects.filter(social_source='http://twitter.com/%s' % screen_name).count() == 0:
                self._parse_statuses(screen_name)
                #else:
                #    latest_coupon = PopularSocialCoupon.objects.filter(social_source='http://twitter.com/%s' % screen_name)\
                #                                                .order_by('-social_item_id')[0]
                #    self._parse_statuses(screen_name, since_id=latest_coupon.social_item_id)