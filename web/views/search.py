import re

from django.db.models import Q
from django.http import HttpResponseRedirect
from core.models import Merchant, Coupon
from web.views.main import render_response
from haystack.query import SearchQuerySet

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def search_model(model, query, fields, order_by="-date_added", objects=None):
    if not objects:
        objects=model.objects
    entry_query = get_query(query.lower(), fields)
    return model.objects.filter(entry_query).order_by(order_by)

def search(request):
    query = request.GET.get("q","").strip()
    merchants = SearchQuerySet().filter(django_ct='core.merchant', content=query,
                                        total_coupon_count__gt=0).order_by('-coupon_count')[:5]
    coupons = SearchQuerySet().filter(django_ct='core.coupon', content=query)[:10]
    merchant_ids = ['core.merchant.%s' % c.merchant_id for c in coupons]
    if merchant_ids:
        relevant_merchants = SearchQuerySet().filter(django_ct='core.merchant', id__in=merchant_ids).order_by('-coupon_count')
    else:
        relevant_merchants = None
    context = {'query': query,
               'merchants': merchants,
               'coupons': coupons,
               'relevant_merchants': relevant_merchants}
    return render_response(template_file="search-results.html", request=request, context=context)