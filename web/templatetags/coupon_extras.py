from django import template
from core.util import print_stack_trace
import urlparse
import urllib

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
        if 'go.redirectingat.com' in url:
            parsed = urlparse.urlparse(url)
            query_dict = urlparse.parse_qs(parsed.query)
            for key in query_dict.keys():
                query_dict[key] = query_dict[key][0]
            if not 'xcust' in query_dict.keys():
                query_dict['xcust'] = ''
            query_dict['xcust'] = context["visitor"].id
            return 'http://go.redirectingat.com/?%s' % urllib.urlencode(query_dict).replace('&','&amp;')
        else:
            return url
    except:
        print_stack_trace()
        return url