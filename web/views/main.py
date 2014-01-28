import json
import datetime
from uuid import uuid4
from django.conf import settings
from django.contrib.flatpages.views import flatpage
from django.contrib.sites.models import get_current_site
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie
from core.models import Category, Coupon, DealType, Merchant, base_description
from core.util import encode_uri_component, print_stack_trace
from core.util.pagination import AlphabeticalPagination
from tracking.views import log_click_track
from tracking.utils import get_visitor_tag
from web.forms import EmailSubscriptionForm
from websvcs.models import EmailSubscription

def render_response(template_file, request, context={}):
    """Shortcut to render function with constant list of parameters"""
    return render_to_response(template_file, context, context_instance=RequestContext(request))


def set_meta_tags(subject, context):
    """Updating context with SEO-related data"""
    context.update(page_title=subject.page_title(),
                   page_description=subject.page_description(),
                   og_title=subject.og_title(),
                   og_description=subject.og_description(),
                   og_image=subject.og_image(),
                   og_url=subject.og_url(),
                   canonical_url=subject.og_url())


@ensure_csrf_cookie
def index(request, current_page=1):
    parameters = {}

    # handling AJAX request 
    if request.is_ajax():
        data = []
        is_new = request.GET.get('is_new', None)
        is_trending = request.GET.get('is_trending', None)
        if is_new:
            parameters['is_new'] = True
        if is_trending:
            parameters['is_popular'] = True
        
        coupons = Coupon.objects.filter(**parameters).order_by("-date_added")
        pages = Paginator(coupons, 12)
        for c in pages.page(current_page).object_list:
            item = {'id': c.id,
                    'merchant_name': c.merchant.name,
                    'short_desc': c.short_desc,
                    'description': c.get_description(),
                    'end': c.end.strftime('%m/%d/%y') if c.end else '',
                    'coupon_type': c.coupon_type,
                    'full_success_path': c.full_success_path(),
                    'image': c.merchant.image}
            data.append(item)
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages}), content_type="application/json")
    
    parameters['is_new'] = True
    coupons = Coupon.objects.filter(**parameters).order_by("-date_added")
    pages = Paginator(coupons, 12)
    
    page = current_page or 1
    if int(page) > pages.num_pages:
        page = pages.num_pages
    ppages = range(1, pages.num_pages+1)
    separators = 0
    if pages.num_pages > 12:
        if page <= 5 or page >= pages.num_pages - 3:
            ppages = ppages[:8] + ppages[-3:]
            separators = 1
        else:
            page_next = current_page + 2
            page_prev = current_page - 2
            ppages = ppages[:3] + ppages[page_prev:page_next] + ppages[-3:]
            separators = 2

    context = {"pages": ppages,
               "num_pages": pages.num_pages,
               "current_page": pages.page(page),
               "separators": separators,
               "coupons": pages.page(page).object_list}

    return render_response("index.html", request, context)


@ensure_csrf_cookie
def top_coupons(request, current_page=1):
    return render_response("top_coupons.html", request, {})


@ensure_csrf_cookie
def coupons_for_company(request, company_name, company_id=None, current_page=None, category_ids=None):
    """List of coupons for given merchant."""
    
    category_ids = request.GET.getlist('category_id', [])
    coupon_types = request.GET.getlist('coupon_type', [])
    sorting = request.GET.get('sorting', None)

    merchant = get_object_or_404(Merchant, name_slug=slugify(company_name))
    if company_id:
        kwargs={'company_name': merchant.name_slug}
        merchant_url = reverse('web.views.main.coupons_for_company', kwargs=kwargs)
        return HttpResponsePermanentRedirect(merchant_url)
    
    all_categories = merchant.get_coupon_categories()
    filters = {'merchant_id': merchant.id}
    
    if category_ids:
        filters['categories__id__in'] = category_ids
    
    if coupon_types:
        filters['coupon_type__in'] = coupon_types

    coupons_list = Coupon.objects.filter(**filters)

    ordering = 'popularity'
    if sorting == 'newest':
        ordering = '-date_added'
    elif sorting == 'expiring_soon':
        ordering = 'end'
    if sorting:
        coupons_list = coupons_list.order_by(ordering)
    
    coupons = list(coupons_list)

    # preparing pagination
    page = current_page or 1
    pages = Paginator(coupons, 12)
    if int(page) > pages.num_pages:
        page = pages.num_pages
    ppages = range(1, pages.num_pages+1)
    separators = 0
    if pages.num_pages > 12:
        if page <= 5 or page >= pages.num_pages - 3:
            ppages = ppages[:8] + ppages[-3:]
            separators = 1
        else:
            page_next = current_page + 2
            page_prev = current_page - 2
            ppages = ppages[:3] + ppages[page_prev:page_next] + ppages[-3:]
            separators = 2
    
    # handling AJAX request 
    if request.is_ajax():
        data = []
        for c in pages.page(page).object_list:
            item = {'id': c.id,
                    'merchant_name': c.merchant.name,
                    'short_desc': c.short_desc,
                    'description': c.get_description(),
                    'end': c.end.strftime('%m/%d/%y') if c.end else '',
                    'full_success_path': c.full_success_path(),
                    'coupon_type': c.coupon_type,
                    'image': c.merchant.image}
            data.append(item)
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages,
                                        'total_items': pages.count}), content_type="application/json")
    
    context = {"coupons": pages.page(page).object_list,
               "merchant": merchant,
               "num_pages": pages.num_pages,
               "pages": ppages,
               "current_page": pages.page(page),
               "num_coupons": pages.count,
               "separators": separators,
               "coupon_categories": all_categories,
               "similar_stores": Merchant.objects.all()[:6]}
    
    set_meta_tags(merchant, context)
    if current_page > 1:
        context['canonical_url'] = "{0}pages/{1}/".format(merchant.og_url(), current_page)

    return render_response("company.html", request, context)


@ensure_csrf_cookie
def redirect_to_open_coupon(request, company_name, coupon_label, coupon_id):
    return HttpResponsePermanentRedirect('{0}/coupons/{1}/{2}/{3}'.format(settings.BASE_URL_NO_APPENDED_SLASH, 
                                                                          company_name, coupon_label, coupon_id))


@ensure_csrf_cookie
def open_coupon(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        log_click_track(request, coupon)
    except Coupon.DoesNotExist:
        raise Http404

    item = {'merchant_name': coupon.merchant.name,
            'merchant_link': coupon.merchant.local_path(),
            'code': coupon.code,
            'short_desc': coupon.short_desc,
            'description': coupon.get_description(),
            'image': coupon.merchant.image,
            'local_path': coupon.local_path(),
            'url': get_visitor_tag(coupon.skimlinks, request.visitor.id)}
    return HttpResponse(json.dumps(item), content_type="application/json")


@ensure_csrf_cookie
def categories(request):
    context={
        "page_description": description,
        "page_title": description,
        "og_title": "Coupon Categories",
        "og_description": description,
        "og_image": icon_url,
        "og_url": "{0}/categories/".format(settings.BASE_URL_NO_APPENDED_SLASH),
        "categories": Category.objects.filter(parent__isnull=True, is_featured=False).order_by('name'),
        "featured_categories": Category.objects.filter(is_featured=True).order_by('name'),
    }
    return render_response("categories.html", request, context)


@ensure_csrf_cookie
def category(request, category_code, current_page=1, category_ids=-1):
    sorting = request.GET.get('sorting', None)
    coupon_types = request.GET.getlist('coupon_type', [])
    current_page = int(current_page)
    category = Category.objects.get(code=category_code, ref_id_source__isnull=True)

    coupon_category_ids = Coupon.objects.filter(categories=category.id).values('categories').annotate()
    category_ids = [c['categories'] for c in coupon_category_ids]
    coupon_categories = Category.objects.filter(id__in=category_ids)

    filters = {'categories__in': category_ids}
    
    if coupon_types:
        filters['coupon_type__in'] = coupon_types

    ordering = 'popularity'
    if sorting == 'newest':
        ordering = '-date_added'
    elif sorting == 'expiring_soon':
        ordering = 'end'

    coupons = Coupon.objects.filter(**filters).order_by(ordering)

    # preparing pagination
    page = current_page or 1
    pages = Paginator(coupons, 12)
    if int(page) > pages.num_pages:
        page = pages.num_pages
    ppages = range(1, pages.num_pages+1)
    separators = 0
    if pages.num_pages > 12:
        if page <= 5 or page >= pages.num_pages - 3:
            ppages = ppages[:8] + ppages[-3:]
            separators = 1
        else:
            page_next = current_page + 2
            page_prev = current_page - 2
            ppages = ppages[:3] + ppages[page_prev:page_next] + ppages[-3:]
            separators = 2
    
    # handling AJAX request 
    if request.is_ajax():
        data = []
        for c in pages.page(current_page).object_list:
            item = {'id': c.id,
                    'merchant_name': c.merchant.name,
                    'short_desc': c.short_desc,
                    'description': c.get_description(),
                    'end': c.end.strftime('%m/%d/%y') if c.end else '',
                    'coupon_type': c.coupon_type,
                    'full_success_path': c.full_success_path(),
                    'image': c.merchant.image}
            data.append(item)
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages,
                                        'total_items': pages.count}), content_type="application/json")
    

    if int(current_page) > pages.num_pages:
        current_page=pages.num_pages

    context = {"num_pages": pages.num_pages,
               "category": category,
               "num_coupons": pages.count,
               "coupon_categories": coupon_categories,
               "coupons": pages.page(page).object_list,
               "pages": ppages,
               "current_page": pages.page(page),
               "num_coupons": pages.count,
               "separators": separators}

    if current_page > 1:
        context['canonical_url'] = "{0}pages/{1}/".format(category.og_url(), current_page)

    return render_response("category.html", request, context)


@ensure_csrf_cookie
def stores(request, page='popular'):
    """List of stores, ordered by alphabet."""

    category = request.GET.get('category', None)
    ordering = '-name'
    if page == '#':
        filters = {'name__regex': r'^[0-9]'}
    elif page == 'popular':
        filters = {'popularity__gt': 0}
        ordering = '-popularity'
    else:
        filters = {'name__istartswith': page}
    if category:
        merchant_ids = [c['merchant__id'] for c in Coupon.objects.filter(categories=category).values('merchant__id').annotate()]
        filters['id__in'] = merchant_ids
    stores = Merchant.objects.filter(**filters).order_by(ordering)
    context={
        "stores": stores,
        "categories": Category.objects.filter(parent__isnull=True, ref_id_source__isnull=True).order_by('name'),
        "category": int(category) if category else None,
        "pagination": AlphabeticalPagination(page),
        "featured_merchants": Merchant.objects.filter(is_featured=True),
        "page": page,
    }
    return render_response("companies.html", request, context)


def email_subscribe(request):
    data = {'success': False}
    if request.method == 'POST':
        instance = EmailSubscription(session_key=request.session.get('key', str(uuid4())), 
                                     app=settings.APP_NAME, source_url=request.META.get('HTTP_REFERER', ''))
        form = EmailSubscriptionForm(data=request.POST, instance=instance)
        if form.is_valid():
            data['success'] = True
            form.save()
        else:
            data['errors'] = form.errors
    return HttpResponse(json.dumps(data), content_type="application/json")
