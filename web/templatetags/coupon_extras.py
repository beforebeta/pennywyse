import urllib
import urlparse
from django import template
from core.util import print_stack_trace
from tracking.utils import get_visitor_tag


register = template.Library()

@register.inclusion_tag('coupon.html')
def show_coupon(coupon):
    return {'coupon': coupon}

@register.inclusion_tag('category_filters.html')
def show_category_filters(categories, form_path):
    return {'categories': categories, 'form_path': form_path}

@register.simple_tag(takes_context=True)
def assign_visitor_tag(context, url):
    try:
        return get_visitor_tag(url, context['visitor'].id)
    except:
        print_stack_trace()
        return url