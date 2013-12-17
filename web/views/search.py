import json
from django.core.paginator import Paginator
from django.http import HttpResponse
from haystack.query import SearchQuerySet
from web.views.main import render_response
from web.utils import FuzzySearchQuerySet

def search(request, current_page=1):
    query = request.GET.get("q","").strip()
    if query:
        merchants = FuzzySearchQuerySet().combined_filter(django_ct='core.merchant',
                                            total_coupon_count__gt=0, content=query)
        coupons_list = SearchQuerySet().filter(django_ct='core.coupon', content=query)
        pages = Paginator(coupons_list, 12)
        if request.is_ajax():
            data = []
            for c in pages.page(current_page).object_list:
                item = {'merchant_name': c.merchant_name,
                        'short_desc': c.short_desc,
                        'description': c.text,
                        'end': c.end.strftime('%m/%d/%y') if c.end else '',
                        'coupon_type': c.coupon_type,
                        'full_success_path': c.full_success_path,
                        'image': c.merchant_image}
                data.append(item)
            return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages}), content_type="application/json")
        coupons = pages.page(current_page).object_list
    else:
        merchants = coupons = None
    context = {'query': query,
               'merchants': merchants,
               'coupons': coupons,
               'query': query}
    return render_response(template_file="search.html", request=request, context=context)