import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from core.models import Coupon, Merchant
from tracking.commission.skimlinks import merchant_slugs

def coupon_tuple(slug, index, base_link, merchant_link):
      merchant = Merchant.objects.get(name_slug=slug)
      coupon = merchant.featured_coupon()
      params = "utm_medium=mailchimp&utm_source=newsletter&utm_campaign=promo&utm_term={0}".format(merchant.name_slug)
      link = "{0}?{1}".format(base_link, params)
      more_merchant_link = "{0}?{1}".format(merchant_link, params)
      return [coupon, index+1, link, more_merchant_link]

def email_a(self):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    i = 0
    date_string = datetime.datetime.now().strftime("%d, %b %Y")
    for slug in merchant_slugs(None):
        merchant = Merchant.objects.get(name_slug=slug)
        coupon = merchant.featured_coupon()
        merchant_link = "http://pennywyse.com/coupons/{0}/{1}".format(merchant.name_slug, merchant.id)
        coupon_data.append(coupon_tuple(slug, i, merchant_link, merchant_link))
        i += 1

    context = {'coupon_data' : coupon_data, 'date_string': date_string, 'show_image': True}
    return render_to_response("email.html", context)

def email_b(self):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    i = 0
    date_string = datetime.datetime.now().strftime("%d, %b %Y")
    for slug in merchant_slugs(None):
        merchant = Merchant.objects.get(name_slug=slug)
        coupon = merchant.featured_coupon()
        merchant_link = "http://pennywyse.com/coupons/{0}/{1}".format(merchant.name_slug, merchant.id)
        coupon_link = "http://pennywyse.com/coupon/{0}/{1}/{2}".format(merchant.name_slug, coupon.desc_slug, coupon.id)
        coupon_data.append(coupon_tuple(slug, i, coupon_link, merchant_link))
        i += 1

    context = {'coupon_data' : coupon_data, 'date_string': date_string, 'show_image': True}
    return render_to_response("email.html", context)

def email_c(self):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    i = 0
    date_string = datetime.datetime.now().strftime("%d, %b %Y")
    for slug in merchant_slugs(None):
        merchant = Merchant.objects.get(name_slug=slug)
        coupon = merchant.featured_coupon()
        merchant_link = "http://pennywyse.com/coupons/{0}/{1}".format(merchant.name_slug, merchant.id)
        coupon_data.append(coupon_tuple(slug, i, merchant_link, merchant_link))
        i += 1

    context = {'coupon_data' : coupon_data, 'date_string': date_string, 'show_image': False}
    return render_to_response("email.html", context)

def email_d(self):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    i = 0
    date_string = datetime.datetime.now().strftime("%d, %b %Y")
    for slug in merchant_slugs(None):
        merchant = Merchant.objects.get(name_slug=slug)
        coupon = merchant.featured_coupon()
        merchant_link = "http://pennywyse.com/coupons/{0}/{1}".format(merchant.name_slug, merchant.id)
        coupon_link = "http://pennywyse.com/coupon/{0}/{1}/{2}".format(merchant.name_slug, coupon.desc_slug, coupon.id)
        coupon_data.append(coupon_tuple(slug, i, coupon_link, merchant_link))
        i += 1

    context = {'coupon_data' : coupon_data, 'date_string': date_string, 'show_image': False}
    return render_to_response("email.html", context)
