import datetime
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from core.models import Coupon, Merchant
from tracking.commission.skimlinks import merchant_slugs

def date_string():
    date_string = datetime.datetime.now().strftime("%d, %b %Y")

def coupon_tuple(link_type):
    coupon_data = []
    index = 0
    for slug in merchant_slugs(None):
        index += 1
        merchant = Merchant.objects.filter(name_slug=slug)[0]
        coupon = merchant.featured_coupon()
        merchant_link = "http://pennywyse.com/coupons/{0}/{1}".format(merchant.name_slug, merchant.id)
        if link_type == 'merchant':
          link_address = merchant_link
        else:
          link_address = "{0}{1}".format(settings.BASE_URL_NO_APPENDED_SLASH, coupon.local_path())
        params = "utm_medium=mailchimp&utm_source=newsletter&utm_campaign=promo&utm_term={0}".format(merchant.name_slug)
        link_address = "{0}?{1}".format(link_address, params)
        merchant_link = "{0}?{1}".format(merchant_link, params)
        coupon_data.append([coupon, index, link_address, merchant_link])
    return coupon_data

def store_description(request):
    desc = request.GET.get('store_description', True)
    if (desc == 'False') | (desc == 'false'):
        return False
    else:
        return True


def email_a(request):
    context = {
        'coupon_data': coupon_tuple('coupon'),
        'date_string': date_string(),
        'show_image': True,
        'store_description': store_description(request)
    }
    return render_to_response("email.html", context)

def email_b(request):
    context = {
        'coupon_data': coupon_tuple('merchant'),
        'date_string': date_string(),
        'show_image': True,
        'store_description': store_description(request)
    }
    return render_to_response("email.html", context)

def email_c(request):
    context = {
        'coupon_data': coupon_tuple('coupon'),
        'date_string': date_string(),
        'show_image': False,
        'store_description': store_description(request)
    }
    return render_to_response("email.html", context)

def email_d(request):
    context = {
        'coupon_data': coupon_tuple('merchant'),
        'date_string': date_string(),
        'show_image': False,
        'store_description': store_description(request)
    }
    return render_to_response("email.html", context)
