from django import template

register = template.Library()

@register.inclusion_tag('coupon.html')
def show_coupon(coupon):
    return {'coupon': coupon}
