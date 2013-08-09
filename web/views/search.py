import re

from django.db.models import Q
from django.http import HttpResponseRedirect
from core.models import Merchant, Coupon
from web.views.main import render_response

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

def search_model(model, query, fields, order_by="-date_added"):
    entry_query = get_query(query.lower(), fields)
    return model.objects.filter(entry_query).order_by(order_by)

def search(request):
    try:
        context={}
        query = request.GET.get("q","").strip()
        context["query"] = query
        merchants = search_model(Merchant, query, ["name"], "-coupon_count")[:5]
        coupons = search_model(Coupon, query, ["description"])[:10]

        context["merchants"] = merchants
        context["coupons"] = coupons
        context["relevant_merchants"] = Merchant.objects.filter(id__in=list(set([c.merchant_id for c in coupons])))
        return render_response(template_file="search-results.html", request=request, context=context)
    except:
        return HttpResponseRedirect("/")
#def search(request):
#    query_string = ''
#    found_entries = None
#    if ('q' in request.GET) and request.GET['q'].strip():
#        query_string = request.GET['q']
#
#        entry_query = get_query(query_string.lower(), ['title', 'body',])
#
#        found_entries = Entry.objects.filter(entry_query).order_by('-pub_date')
#
#    return render_to_response('search/search_results.html',
#            { 'query_string': query_string, 'found_entries': found_entries },
#        context_instance=RequestContext(request))
