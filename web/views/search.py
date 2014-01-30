import json
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from haystack.query import SearchQuerySet
from core.models import Merchant
from web.views.main import render_response
from web.utils import FuzzySearchQuerySet

def search(request, current_page=1):
    query = request.GET.get("q","").strip()
    coupon_type = request.GET.get('coupon_type', None)
    is_new = request.GET.get('is_new', None)
    is_trending = request.GET.get('is_trending', None)
    
    if query:
        merchant = Merchant.objects.filter(name=query).only('name_slug')
        if merchant.count() == 1:
            merchant_url = reverse('web.views.main.coupons_for_company', kwargs={'company_name': merchant[0].name_slug})
            return HttpResponseRedirect(merchant_url)
        parameters = {'django_ct':'core.coupon', 'content':query}
        if is_new:
            parameters['is_new'] = True
        if is_trending:
            parameters['is_popular'] = True
        if coupon_type:
            parameters['coupon_type'] = coupon_type
        merchants_list = FuzzySearchQuerySet().combined_filter(django_ct='core.merchant',
                                            total_coupon_count__gt=0, content=query)
        coupons_list = SearchQuerySet().filter(**parameters)
        pages = Paginator(coupons_list, 12)
        merchant_pages = Paginator(merchants_list, 10)
        if request.is_ajax():
            data = []
            fetch_merchants = request.GET.get('fetch_merchants', None)
            if fetch_merchants:
                try:
                    for m in merchant_pages.page(current_page).object_list:
                        item = {'local_path': m.local_path,
                                'image': m.image}
                        data.append(item)
                except:
                    pass
            else:
                try:
                    for c in pages.page(current_page).object_list:
                        item = {'merchant_name': c.merchant_name,
                                'short_desc': c.short_desc,
                                'description': c.text,
                                'end': c.end.strftime('%m/%d/%y') if c.end else '',
                                'coupon_type': c.coupon_type,
                                'full_success_path': c.full_success_path,
                                'image': c.merchant_image,
                                'id': c.pk,
                                'code': c.code}
                        data.append(item)
                except:
                    pass
                    
            return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages}), content_type="application/json")
        merchants = merchant_pages.page(current_page).object_list
    else:
        merchants = None
    context = {'query': query,
               'merchants': merchants}
    return render_response(template_file="search.html", request=request, context=context)