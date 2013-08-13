import pdb
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from core.models import Coupon, Merchant
from tracking.commission.skimlinks import _merchant_descriptions

def email(self):
    all_coupons = Coupon.objects.all()
    coupon_data = []
    i = 0
    for slug in _merchant_descriptions.keys():
        coupon = Merchant.objects.get(name_slug=slug).featured_coupon()
        coupon_data.append([coupon, i + 1])
        i += 1

    context = {'coupon_data' : coupon_data}
    return render_to_response("email.html", context)
