from django import template

register = template.Library()

@register.inclusion_tag('email/coupon.html')
def show_coupon(coupon):
    return {'coupon': coupon[0], 'index': coupon[1], 'coupon_url': coupon[2], 'merchant_url': coupon[3]}
