import json
from uuid import uuid4
from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie
from constance import config
from core.models import Category, Coupon, Merchant
from core.util import adaptive_cache_page, CustomPaginator
from core.util.pagination import AlphabeticalPagination
from tracking.views import log_click_track
from tracking.utils import get_visitor_tag
from web.forms import EmailSubscriptionForm
from websvcs.models import EmailSubscription

SORTING_MAPPING = {'newest': '-date_added',
                   'new': '-date_added',
                   'expiring_soon': 'end',
                   'trending': 'popularity'}


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
@adaptive_cache_page
def index(request, current_page=None):
    """Landing page controller."""
    
    parameters = {'is_active': True, 'is_featured': True}
    page = int(current_page or 1)
    sorting = request.GET.get('sorting', None)

    # handling AJAX request 
    if request.is_ajax():
        data = []
        coupon_types = request.GET.getlist('coupon_type', [])
        if coupon_types:
            parameters['coupon_type__in'] = coupon_types
        ordering = SORTING_MAPPING.get(sorting, '-date_added')        
        coupons = Coupon.objects.filter(**parameters)\
                                .only('id', 'short_desc', 'description', 'end', 'coupon_type', 'merchant')\
                                .order_by(ordering)\
                                .exclude(merchant__s3_image='http://pushpenny.s3.amazonaws.com/static/img/favicon.png')[:400]
        pages = Paginator(coupons, 20)
        try:
            for c in pages.page(page).object_list:
                item = {'id': c.id,
                        'short_desc': c.short_desc,
                        'description': c.description,
                        'end': c.end.strftime('%m/%d/%y') if c.end else '',
                        'coupon_type': c.coupon_type,
                        'full_success_path': c.full_success_path(),
                        'image': c.merchant.s3_image,
                        'twitter_share_url': c.twitter_share_url,
                        'merchant_link': c.merchant.local_path()}
                data.append(item)
        except EmptyPage:
            raise Http404
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages}), content_type="application/json")
    
    
    coupons = Coupon.objects.filter(**parameters)\
                            .only('id', 'short_desc', 'description', 'end', 'coupon_type', 'merchant__name_slug',
                                  'merchant__s3_image', 'merchant__name')\
                            .exclude(merchant__s3_image='http://pushpenny.s3.amazonaws.com/static/img/favicon.png')\
                            .order_by("-date_added")[:400]
    pages = CustomPaginator(coupons, 20, current_page=page)
    
    try:
        items = pages.page(page).object_list
        cpage = pages.page(page)
    except EmptyPage:
        items = cpage = None
    # permanently redirecting from first pagination page to canonical URL
    # or if current pagination page does not exist any more
    if (not items and coupons.count() > 0) or (current_page and int(current_page) == 1) or\
        (not items and coupons.count() == 0 and page != 1):
        return HttpResponsePermanentRedirect(reverse('web.views.main.index'))
    
    context = {"pages": pages.separated_pages,
               "num_pages": pages.num_pages,
               "current_page": cpage,
               "separators": pages.separators,
               "coupons": items}

    return render_response("index.html", request, context)


@ensure_csrf_cookie
def top_coupons(request, current_page=1):
    """
    Dedicated page with same content as corresponding navigation menu section "Top Coupons".
    Available from mobile site layout only.
    """
    return render_response("top_coupons.html", request, {})


@ensure_csrf_cookie
@adaptive_cache_page(assign_visitor_tag=True)
def coupons_for_company(request, company_name, company_id=None, current_page=None, category_ids=None):
    """List of coupons for given merchant."""
    
    category_ids = request.GET.getlist('category_id', [])
    coupon_types = request.GET.getlist('coupon_type', [])
    coupon_id = request.GET.get('c', None)
    sorting = request.GET.get('sorting', None)

    try:
        merchant = Merchant.objects.only('id', 'name', 'name_slug', 'skimlinks',
                                         'link', 's3_image', 'similar').get(name_slug=slugify(company_name))
    except Merchant.DoesNotExist:
        raise Http404
    
    # if company ID provided, permanently redirecting to URL without ID
    if company_id:
        kwargs={'company_name': merchant.name_slug}
        merchant_url = reverse('web.views.main.coupons_for_company', kwargs=kwargs)
        return HttpResponsePermanentRedirect(merchant_url)
    
    filters = {'merchant_id': merchant.id, 'is_active': True}
    
    if category_ids:
        filters['categories__id__in'] = category_ids
    
    if coupon_types:
        filters['coupon_type__in'] = coupon_types

    page = int(current_page or 1)
    ordering = SORTING_MAPPING.get(sorting, 'popularity')

    # handling AJAX request 
    if request.is_ajax():
        coupons_list = Coupon.objects.filter(**filters)\
                                    .only('id', 'short_desc', 'description', 'end', 'coupon_type', 'merchant', 'image')
        coupons = coupons_list.order_by(ordering)
    
        # preparing pagination
        pages = Paginator(coupons, 20)
        data = []
        try:
            for c in pages.page(page).object_list:
                item = {'id': c.id,
                        'merchant_name': merchant.name,
                        'short_desc': c.short_desc,
                        'description': c.description,
                        'end': c.end.strftime('%m/%d/%y') if c.end else '',
                        'full_success_path': c.full_success_path(),
                        'coupon_type': c.coupon_type,
                        'image': c.s3_image,
                        'twitter_share_url': c.twitter_share_url}
                data.append(item)
        except EmptyPage:
            raise Http404
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages,
                                        'total_items': pages.count}), content_type="application/json")

    # fetching coupons only if coupon ID provided
    coupon = None
    if coupon_id:
        coupon = Coupon.objects.get(id=coupon_id)
    
    all_categories_ids = [c['categories'] for c in Coupon.objects.filter(merchant=merchant.id).values('categories').annotate()]
    all_categories = Category.objects.only('id', 'name')\
                                        .filter(id__in=all_categories_ids)
    coupons = Coupon.objects.filter(**filters)\
                            .only('id', 'short_desc', 'description', 'end', 'coupon_type', 's3_image',
                                  'merchant__name_slug', 'merchant__s3_image', 'merchant__name')\
                            .order_by(ordering)
    pages = CustomPaginator(coupons, 20, current_page=page)
    try:
        items = pages.page(page).object_list
        cpage = pages.page(page)
    except EmptyPage:
        items = cpage = None
    
    # permanently redirecting from first pagination page to canonical URL
    # or if current pagination page does not exist any more
    if (not items and coupons.count() > 0) or (current_page and int(current_page) == 1) or\
        (not items and coupons.count() == 0 and page != 1):
        return HttpResponsePermanentRedirect(reverse('web.views.main.coupons_for_company', 
                                                     kwargs={'company_name': merchant.name_slug,
                                                             'company_id': merchant.id}))
    
    context = {"coupons": items,
               "merchant": merchant,
               "num_pages": pages.num_pages,
               "pages": pages.separated_pages,
               "current_page": cpage,
               "num_coupons": pages.count,
               "separators": pages.separators,
               "coupon_categories": all_categories,
               "coupon": coupon}
    
    set_meta_tags(merchant, context)
    return render_response("company.html", request, context)


@ensure_csrf_cookie
def redirect_to_open_coupon(request, company_name, coupon_label, coupon_id):
    """Fallback for old coupon URLs for redirection to new ones."""
    
    coupons = Coupon.objects.filter(id=coupon_id)
    if len(coupons) > 0:
        coupon = coupons[0]
    else:
        coupons = Coupon.objects.filter(desc_slug=coupon_label)
        if len(coupons) > 0:
            coupon = coupons[0]
        else:
            raise Http404     
    return HttpResponsePermanentRedirect(coupon.local_path())


@ensure_csrf_cookie
def open_coupon(request, coupon_id):
    """Fetching coupon by given coupon ID and logging it if successful."""
    
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        log_click_track(request, coupon)
    except Coupon.DoesNotExist:
        raise Http404

    item = {'merchant_name': coupon.merchant.name,
            'merchant_link': get_visitor_tag(coupon.merchant.skimlinks, request.session['visitor_id']),
            'code': coupon.code,
            'short_desc': coupon.short_desc,
            'description': coupon.description,
            'image': coupon.merchant.s3_image,
            'local_path': coupon.local_path(),
            'url': get_visitor_tag(coupon.skimlinks, request.session['visitor_id']),
            'twitter_share_url': coupon.twitter_share_url,
            'full_success_path': coupon.full_success_path()}
    return HttpResponse(json.dumps(item), content_type="application/json")

def redirect_to_affiliate_url(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        log_click_track(request, coupon)
    except Coupon.DoesNotExist:
        raise Http404
    affiliate_url = get_visitor_tag(coupon.skimlinks, request.session['visitor_id'])
    return redirect(affiliate_url)

@ensure_csrf_cookie
@cache_page(60 * 60 * 24)
def categories(request):
    """Lists of parent and featured categories."""
    
    context = {"categories": Category.objects.filter(is_featured=False, parent__isnull=True, ref_id_source__isnull=True)\
                                                .only('name', 'icon', 'code')\
                                                .order_by('name'),
               "featured_categories": Category.objects.filter(is_featured=True, ref_id_source__isnull=True)\
                                                       .only('name', 'icon', 'code')\
                                                       .order_by('name'),
               "CATEGORIES_PAGE_TEXT": getattr(config, 'CATEGORIES_PAGE_TEXT', None)}
    return render_response("categories.html", request, context)


@ensure_csrf_cookie
@cache_page(60 * 60 * 24)
def groceries(request):
    """Dedicated controller with list of grocery categories."""
    
    root_category = get_object_or_404(Category, code='grocery')
    grocery_categories = Category.objects.filter(parent=root_category, ref_id_source__isnull=True)\
                                            .only('name', 'icon', 'code')
    categories = [root_category] + list(grocery_categories)
    context = {'categories': categories,
               'is_grocery': True,
               'GROCERIS_PAGE_TEXT': getattr(config, 'GROCERIS_PAGE_TEXT', None)}
    return render_response("categories.html", request, context)



@ensure_csrf_cookie
@adaptive_cache_page
def category(request, category_code, current_page=None, category_ids=-1):
    """List of coupons for given category."""
    
    sorting = request.GET.get('sorting', None)
    coupon_types = request.GET.getlist('coupon_type', [])

    try:
        category = Category.objects.only('id', 'name', 'code', 'icon')\
                            .get(code=category_code, ref_id_source__isnull=True)
    except Category.DoesNotExist:
        raise Http404

    coupon_category_ids = Coupon.objects.filter(categories=category.id).values('categories').annotate()
    category_ids = [c['categories'] for c in coupon_category_ids]
    coupon_categories = Category.objects.filter(id__in=category_ids)

    filters = {'categories__in': category_ids, 'is_active': True}
    
    if coupon_types:
        filters['coupon_type__in'] = coupon_types

    ordering = SORTING_MAPPING.get(sorting, 'popularity')
    page = int(current_page or 1)
    
    # handling AJAX request 
    if request.is_ajax():
        data = []
        coupons = Coupon.objects.filter(**filters).order_by(ordering)\
                                 .only('id', 'short_desc', 'description', 'end', 'coupon_type', 'merchant')
        pages = Paginator(coupons, 20)
        try:
            for c in pages.page(page).object_list:
                item = {'id': c.id,
                        'merchant_name': c.merchant.name,
                        'short_desc': c.short_desc,
                        'description': c.description,
                        'end': c.end.strftime('%m/%d/%y') if c.end else '',
                        'coupon_type': c.coupon_type,
                        'full_success_path': c.full_success_path(),
                        'image': c.merchant.s3_image,
                        'twitter_share_url': c.twitter_share_url,
                        'merchant_link': c.merchant.local_path()}
                data.append(item)
        except EmptyPage:
            raise Http404
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages,
                                        'total_items': pages.count}), content_type="application/json")
    
    coupons = Coupon.objects.filter(**filters)\
                            .only('id', 'short_desc', 'description', 'end', 'coupon_type', 's3_image',
                                  'merchant__name_slug', 'merchant__s3_image', 'merchant__name')\
                            .order_by(ordering)
    pages = CustomPaginator(coupons, 20, current_page=page)
    try:
        items = pages.page(page).object_list
        cpage = pages.page(page)
    except EmptyPage:
        items = cpage = None 
    # permanently redirecting from first pagination page to canonical URL
    # or if current pagination page does not exist any more
    if (not items and coupons.count() > 0) or (current_page and int(current_page) == 1) or\
        (not items and coupons.count() == 0 and page != 1):
        return HttpResponsePermanentRedirect(reverse('web.views.main.category', 
                                                     kwargs={'category_code': category.code}))

    context = {"num_pages": pages.num_pages,
               "category": category,
               "num_coupons": pages.count,
               "coupon_categories": coupon_categories,
               "coupons": items,
               "pages": pages.separated_pages,
               "current_page": cpage,
               "num_coupons": pages.count,
               "separators": pages.separators}
    return render_response("category.html", request, context)


@ensure_csrf_cookie
@cache_page(60 * 60 * 24)
def stores(request, page='popular'):
    """List of stores, ordered by alphabet."""

    category = request.GET.get('category', None)
    ordering = 'name'
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
    stores = Merchant.objects.only('name', 'name_slug')\
                                .filter(**filters).order_by(ordering)
    context = {"stores": stores,
                "pagination": AlphabeticalPagination(page),
                "featured_merchants": Merchant.objects.only('name', 'name_slug', 's3_image')\
                                                        .filter(is_featured=True),
                "page": page,
                "MERCHANTS_PAGE_TEXT": getattr(config, 'MERCHANTS_PAGE_TEXT', None)}
    return render_response("companies.html", request, context)


def email_subscribe(request):
    """Controller for handling email subscription via AJAX request."""
    
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


@cache_page(60 * 60 * 24)
def not_found(request):
    """404 page handler."""
    
    response = render_response("not_found.html", request, {})
    response.status_code = 404
    return response