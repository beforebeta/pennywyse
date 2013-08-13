import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from core.models import Coupon, Merchant
from tracking.commission.skimlinks import _merchant_descriptions

def email_a(self):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    i = 0
    date_string = datetime.datetime.now().strftime("%d, %b %Y")
    for slug in _merchant_descriptions.keys():
        merchant = Merchant.objects.get(name_slug=slug)
        coupon = merchant.featured_coupon()
        params = "utm_medium=mailchimp&utm_source=newsletter&utm_campaign=promo&utm_term={0}".format(merchant.name_slug)
        link = "{0}?{1}".format(coupon.link, params)
        coupon_data.append([coupon, i + 1, link])
        i += 1

    context = {'coupon_data' : coupon_data, 'date_string': date_string}
    return render_to_response("email.html", context)

def email_b(self):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    i = 0
    date_string = datetime.datetime.now().strftime("%d, %b %Y")
    for slug in _merchant_descriptions.keys():
        merchant = Merchant.objects.get(name_slug=slug)
        coupon = merchant.featured_coupon()
        params = "utm_medium=mailchimp&utm_source=newsletter&utm_campaign=promo&utm_term={0}".format(merchant.name_slug)
        link = "{0}?{1}".format(merchant.link, params)
        coupon_data.append([coupon, i + 1, link])
        i += 1

    context = {'coupon_data' : coupon_data, 'date_string': date_string}
    return render_to_response("email.html", context)
