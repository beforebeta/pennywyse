import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from core.models import Coupon, Merchant
from tracking.commission.skimlinks import merchant_slugs

def date_string():
    date_string = datetime.datetime.now().strftime("%d, %b %Y")

def coupon_tuple(link_type):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    index = 0
    for slug in merchant_slugs(None):
        index += 1
        merchant = Merchant.objects.get(name_slug=slug)
        coupon = merchant.featured_coupon()
        merchant_link = "http://pennywyse.com/coupons/{0}/{1}".format(merchant.name_slug, merchant.id)
        link_address = None
        if link_type == 'merchant':
          link_address = merchant_link
        else:
          link_address = "http://pennywyse.com/coupon/{0}/{1}/{2}".format(merchant.name_slug, coupon.desc_slug, coupon.id)
        params = "utm_medium=mailchimp&utm_source=newsletter&utm_campaign=promo&utm_term={0}".format(merchant.name_slug)
        link_address = "{0}?{1}".format(link_address, params)
        merchant_link = "{0}?{1}".format(merchant_link, params)
        coupon_data.append([coupon, index, link_address, merchant_link])
    return coupon_data

def email_a(self):
    context = {
        'coupon_data' : coupon_tuple('coupon'),
        'date_string': date_string(),
        'show_image': True,
    }
    return render_to_response("email.html", context)

def email_b(self):
    context = {
        'coupon_data' : coupon_tuple('merchant'),
        'date_string': date_string(),
        'show_image': True
    }
    return render_to_response("email.html", context)

def email_c(self):
    context = {
        'coupon_data' : coupon_tuple('coupon'),
        'date_string': date_string(),
        'show_image': False
    }
    return render_to_response("email.html", context)

def email_d(self):
    context = {
        'coupon_data' : coupon_tuple('merchant'),
        'date_string': date_string(),
        'show_image': False
    }
    return render_to_response("email.html", context)
