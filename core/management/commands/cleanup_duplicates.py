from BeautifulSoup import BeautifulStoneSoup
import datetime
from lxml import etree
from optparse import make_option
from urlparse import urlparse, parse_qs

from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Category, Country, Coupon, DealType, Merchant, MerchantAffiliateData
from django.db.models import Count

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--check', action='store_true', dest='check', default=False),
        make_option('--cleanup', action='store_true', dest='cleanup', default=False),
    )

    def handle(self, *args, **options):
        if options.get('check', None):
            duplicated_merchants = Merchant.objects.values('name').annotate(duplicates=Count('name')).filter(duplicates__gt=1)
            duplicated_coupons = Coupon.objects.values('ref_id').annotate(duplicates=Count('ref_id')).filter(duplicates__gt=1).count()
            print 'Duplicated merchants: %s' % duplicated_merchants.count()
            if duplicated_merchants:
                for m in duplicated_merchants:
                    print '%s (%s)' % (m['name'], m['duplicates'])
            print 'Duplicated coupons: %s' % duplicated_coupons
        
        if options.get('cleanup', None):
            # cleaning up duplicated merchants
            merchant_data = Merchant.objects.values('name').annotate(duplicates=Count('name')).filter(duplicates__gt=1)
            for data in merchant_data:
                merchants = Merchant.objects.filter(name=data['name']).order_by('id')
                merchant = merchants[0]
                duplicates_data = ['%s (%s)' % (m.name, m.id) for m in merchants[1:]]
                for duplicated_merchant in merchants[1:]:
                    updated_coupons = Coupon.objects.filter(merchant=duplicated_merchant).update(merchant=merchant)
                    print 'Moved %s coupons from %s(%s) merchant to %s(%s)' % (updated_coupons, duplicated_merchant.name,
                                                                               duplicated_merchant.id, merchant.name,
                                                                               merchant.id) 
                    duplicated_merchant.delete()
                print 'Removed duplicated merchants: %s' % ','.join(duplicates_data)
            
            # cleaning up duplicated coupons
            coupon_data = Coupon.objects.values('ref_id').annotate(duplicates=Count('ref_id')).filter(duplicates__gt=1)
            for data in coupon_data:
                coupons =  Coupon.objects.filter(ref_id=data['ref_id']).order_by('id')
                coupon = coupons[0]
                for duplicated_coupon in coupons[1:]:
                    print 'Removed duplicated coupon ID - %s, ref_id - %s' % (duplicated_coupon.id, duplicated_coupon.ref_id)
                    if ClickTrack.objects.filter(coupon=duplicated_coupon).count() > 0:
                        print 'updated clicktracks %s' % ClickTrack.objects.filter(coupon=duplicated_coupon).update(coupon=coupon)
                   if FeaturedCoupon.objects.filter(coupon=duplicated_coupon).count() > 0:
                        print 'updated featured coupons %s' % FeaturedCoupon.objects.filter(coupon=duplicated_coupon).update(coupon=coupon)
                    if NewCoupon.objects.filter(coupon=duplicated_coupon).count() > 0:
                        print 'updated new coupons %s' % NewCoupon.objects.filter(coupon=duplicated_coupon).update(coupon=coupon)
                    if PopularCoupon.objects.filter(coupon=duplicated_coupon).count() > 0:
                        print 'updated popular coupons %s' % PopularCoupon.objects.filter(coupon=duplicated_coupon).update(coupon=coupon)
                ids = [c.id for c in coupons[1:]]
                print Coupon.objects.filter(id__in=ids).delete()
