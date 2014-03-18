import json
import time
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from haystack.query import SearchQuerySet
from redis import Redis
from core.models import Merchant
from web.views.main import render_response, SORTING_MAPPING
from web.utils import FuzzySearchQuerySet

def search(request, current_page=1):
    query = request.GET.get("q","").strip()
    coupon_type = request.GET.get('coupon_type', None)
    sorting = request.GET.get('sorting', None)
    ordering = SORTING_MAPPING.get(sorting, 'popularity')
    context = {}
    
    if query:
        merchant = Merchant.objects.filter(name=query).only('name_slug')
        if merchant.count() == 1:
            redis = Redis()
            redirection_data = {'visitor_id': request.session.get('visitor_id', None),
                                'merchant_id': merchant[0].id,
                                'date_added': time.time()}
            redis.set('redirection_data_%s' % request.session.get('visitor_id', None), json.dumps(redirection_data))
            merchant_url = reverse('web.views.main.coupons_for_company', kwargs={'company_name': merchant[0].name_slug})
            return HttpResponseRedirect(merchant_url)
        parameters = {'django_ct':'core.coupon', 'content':query}
        if coupon_type:
            parameters['coupon_type'] = coupon_type
        merchants_list = FuzzySearchQuerySet().combined_filter(django_ct='core.merchant',
                                            total_coupon_count__gt=0, content=query)
        if not merchants_list:
            context['suggested_merchants'] = Merchant.objects.filter(is_featured=True)[:5]
        coupons_list = SearchQuerySet().filter(**parameters).order_by(ordering)
        pages = Paginator(coupons_list, 20)
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
                                'code': c.code,
                                'merchant_link': c.merchant_local_path}
                        data.append(item)
                except:
                    pass
                    
            return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages}), content_type="application/json")
        merchants = merchant_pages.page(current_page).object_list
        context['coupons'] = pages.page(current_page).object_list
    else:
        merchants = None
    context.update(query=query, merchants=merchants)
    return render_response(template_file="search.html", request=request, context=context)