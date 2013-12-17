import json
import random
import re
import string
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie
from core.models import Category, Coupon, Merchant, base_description
from core.util import encode_uri_component, print_stack_trace
from core.util.pagination import AlphabeticalPagination
from tracking.views import log_click_track
from tracking.utils import get_visitor_tag
from web.models import ShortenedURLComponent


def build_base_context(request, context):
    merchants_data = []
    
    # aggregating merchants - first three merchants, starting with every alphabet letter
    merchants = Merchant.objects.values('id', 'name', 'name_slug')
    for char in list(string.uppercase):
        i = 0
        for m in merchants:
            if i <= 2 and m['name'].startswith(char):
                merchants_data.append(m)
                i += 1
            if i > 2:
                break

    base_context = {"visitor": getattr(request, 'visitor', None),
               "top_merchants": merchants_data,
                "top_categories": Category.objects.filter(parent__isnull=True)[:6],
                "top_groceries": Category.objects.filter(name='Grocery Coupons')[0],}
    context.update(**base_context)
    return context

def render_response(template_file, request, context={}):
    build_base_context(request, context)
    return render_to_response(template_file, context, context_instance=RequestContext(request))

def set_active_tab(active_tab, context):
    if active_tab == "category":
        context['category_tab_class'] = 'active'
    elif active_tab == "company":
        context['company_tab_class'] = 'active'
    elif active_tab == "blog":
        context['blog_tab_class'] = 'active'
    elif active_tab == "stores":
        context['stores_tab_class'] = 'active'
    else:
        context['coupon_tab_class'] = 'active'

def set_meta_tags(subject, context):
    context["page_title"] = subject.page_title()
    context["page_description"] = subject.page_description()
    context["og_title"] = subject.og_title()
    context["og_description"] = subject.og_description()
    context["og_image"] = subject.og_image()
    context["og_url"] = subject.og_url()
    context["canonical_url"] = subject.og_url()

def set_canonical_url(request, context):
    full_path = request.get_full_path()
    canonical_path = re.search('[A-z0-9\/\-]+', full_path).group(0)

    context["canonical_url"] = (settings.BASE_URL_NO_APPENDED_SLASH + canonical_path)


@ensure_csrf_cookie
#@cache_page(60 * 60 * 24)
def index(request, current_page=1):
    # handling AJAX request 
    if request.is_ajax():
        data = []
        parameters = {}
        is_new = request.GET.get('is_new', None)
        is_tranding = request.GET.get('is_tranding', None)
        if is_new:
            parameters['is_new'] = True
        if is_tranding:
            parameters['is_popular'] = True
        coupons = Coupon.objects.filter(**parameters).order_by("-date_added")
        pages = Paginator(coupons, 12)
        for c in pages.page(current_page).object_list:
            item = {'merchant_name': c.merchant.name,
                    'short_desc': c.short_desc,
                    'description': c.get_description(),
                    'end': c.end.strftime('%m/%d/%y') if c.end else '',
                    'coupon_type': c.coupon_type,
                    'full_success_path': c.full_success_path(),
                    'image': c.merchant.get_image()}
            data.append(item)
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages}), content_type="application/json")
    
    context = {
      "page_title": base_description,
      "page_description": base_description,
      "og_title": "PushPenny",
      "og_description": "Hand Verified Coupon Codes",
      "og_url": settings.BASE_URL_NO_APPENDED_SLASH,
      "new_coupons": Coupon.objects.filter(is_new=True).order_by("-date_added")[:8],
      "pop_coupons": Coupon.objects.filter(is_popular=True).order_by("-date_added")[:8],
    }

    set_canonical_url(request, context)
    return render_response("index.html", request, context)

def _search(itm,lst,f):
    for l in lst:
        if f(itm,l):
            return True
    return False

@ensure_csrf_cookie
def coupons_for_company(request, company_name, company_id=None, current_page=None, category_ids=-1):
    """List of coupons for given merchant."""
    
    category_ids = request.GET.getlist('category_id', [])
    coupon_types = request.GET.getlist('coupon_type', [])
    sorting = request.GET.get('sorting', None)

    merchant = None
    if company_id:
        try:
            merchant = Merchant.objects.get(id=company_id)
        except Merchant.DoesNotExist:
            pass
    if not merchant:
        merchant = Merchant.objects.filter(name_slug= slugify(company_name)).order_by("-id")
        if not merchant:
            raise Http404
        # if merchant wasn't found by ID - redirecting to merchant page URL with proper ID in it
        kwargs={'company_name': merchant[0].name_slug,
                'company_id': merchant[0].id}
        if current_page > 1:
            kwargs['current_page'] = current_page
        original_merchant_url = reverse('web.views.main.coupons_for_company', kwargs=kwargs)
        return HttpResponsePermanentRedirect(original_merchant_url)

    if current_page and int(current_page) == 1:
        return HttpResponsePermanentRedirect(reverse('web.views.main.coupons_for_company', 
                                                     kwargs={'company_name': merchant.name_slug,
                                                             'company_id': merchant.id}))

    all_categories = merchant.get_coupon_categories()
    coupons_list = merchant.get_active_coupons()
    if category_ids:
        coupons_list.filter(Q(categories__id__in=category_ids) |\
                            Q(categories__id__isnull=True))
    
    if coupon_types:
        coupons_list.filter(dealtypes__code__in=coupon_types)
 
    ordering = 'popularity'
    if sorting == 'newest':
        ordering = '-date_added'
    elif sorting == 'expiring_soon':
        ordering = 'end'
    if sorting:
        coupons_list = coupons_list.order_by(ordering)
    coupons = list(coupons_list)
    expired_coupons = list(merchant.get_expired_coupons())
    coupons += expired_coupons

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
            item = {'merchant_name': c.merchant.name,
                    'short_desc': c.short_desc,
                    'description': c.get_description(),
                    'end': c.end.strftime('%m/%d/%y') if c.end else '',
                    'coupon_type': c.coupon_type,
                    'full_success_path': c.full_success_path()}
            data.append(item)
        return HttpResponse(json.dumps({'items': data,
                                        'total_pages': pages.num_pages}), content_type="application/json")
    
    context = {
        "merchant"              : merchant,
        "pages"                 : ppages,
        "num_pages"             : pages.num_pages,
        "current_page"          : pages.page(page),
        "current_page_idx"      : int(page),
        "separators"            : separators,
        "coupons"               : pages.page(page).object_list,
        "num_coupons"           : pages.count,
        "total_coupon_count"    : merchant.coupon_count + len(expired_coupons),
        "coupon_categories"     : all_categories,
        "similar_stores"        : Merchant.objects.all()[:6],
    }
    set_meta_tags(merchant, context)
    if current_page > 1:
        context['canonical_url'] = "{0}pages/{1}/".format(merchant.og_url(), current_page)

    return render_response("company.html", request, context)

@ensure_csrf_cookie
def redirect_to_open_coupon(request, company_name, coupon_label, coupon_id):
    return HttpResponsePermanentRedirect('{0}/coupons/{1}/{2}/{3}'.format(settings.BASE_URL_NO_APPENDED_SLASH, company_name, coupon_label, coupon_id))

@ensure_csrf_cookie
def open_coupon(request, company_name, coupon_label, coupon_id):
    log_click_track(request)
    try:
        coupon = Coupon.objects.get(id=coupon_id)
    except Coupon.DoesNotExist:
        coupon = Coupon.objects.filter(desc_slug=coupon_label).order_by('-id')
        if not coupon:
            raise Http404
        original_coupon_url = reverse('web.views.main.open_coupon', kwargs={'company_name': company_name,
                                                                            'coupon_label': coupon_label,
                                                                            'coupon_id': coupon[0].id})
        return HttpResponsePermanentRedirect(original_coupon_url)

    if coupon.merchant.redirect:
        if coupon.merchant.use_skimlinks:
            coupon_url = get_visitor_tag(coupon.skimlinks, request.visitor.id)
        else:
            coupon_url = coupon.link
        return HttpResponseRedirect(coupon_url)

    logo_url = "/"
    back_url = "/"
    try:
        logo_url = request.META["HTTP_REFERER"]
        back_url = logo_url
        if "localhost" not in logo_url and "pushpenny.com" not in logo_url:
            logo_url="/"
    except:
        pass

    context={
        "coupon"        : coupon,
        "logo_url"      : logo_url,
        "back_url"      : back_url,
        "path"          : encode_uri_component("%s://%s%s" % ("http", "www.pushpenny.com", request.path)),
    }
    set_meta_tags(coupon, context)

    return render_response("open_coupon.html",request, context)

@ensure_csrf_cookie
@cache_page(60 * 60 * 24)
def privacy(request):
    return render_response("privacy.html", request, {})

@ensure_csrf_cookie
@cache_page(60 * 60 * 24)
def categories(request):
    description = "Coupon Categories | {0}".format(base_description)
    context={
        "categories": Category.objects.filter(ref_id_source__isnull=True, parent__isnull=True, is_featured=False).order_by('name'),
        "featured_categories": Category.objects.filter(ref_id_source__isnull=True, parent__isnull=True, is_featured=True).order_by('name'),
        "page_description": description,
        "page_title": description,
        "og_title": "Coupon Categories",
        "og_description": description,
        "og_image": icon_url,
        "og_url": "{0}/categories/".format(settings.BASE_URL_NO_APPENDED_SLASH),
    }
    set_active_tab('category', context)
    set_canonical_url(request, context)

    return render_response("categories.html", request, context)

@ensure_csrf_cookie
@cache_page(60 * 60 * 24)
def category(request, category_code, current_page=1, category_ids=-1):
    current_page = int(current_page)
    category = Category.objects.get(code=category_code, ref_id_source__isnull=True)

    if category_ids == -1:
        all_categories = [str(x["categories__id"]) for x in category.get_active_coupons().values("categories__id") if x["categories__id"]]
        selected_categories = ",".join(set(all_categories))
    else:
        selected_categories = category_ids
    comma_categories = selected_categories

    if request.POST:
        category_ids = []
        for param in request.POST:
            try:
                category_ids.append(str(int(param)))
            except:
                pass
        category_ids = ",".join(category_ids)
    else:
        category_ids = str(category.id)

    try:
        selected_categories=[int(s) for s in category_ids.split(",") if s]
    except:
        selected_categories=[]
    all_categories = category.get_coupon_categories()
    coupon_categories = []
    for coup_cat in all_categories:
        coupon_categories.append({
            "category"  : coup_cat,
            "active"    : _search(coup_cat.id, selected_categories, lambda a,b:a==b)
        })

    pages = category.coupons_in_categories(selected_categories)
    ppages = range(1, pages.num_pages+1)
    separators = 0
    if pages.num_pages > 12:
        if current_page <= 5 or current_page >= pages.num_pages - 3:
            ppages = ppages[:8] + ppages[-3:]
            separators = 1
        else:
            page_next = current_page + 2
            page_prev = current_page - 2
            ppages = ppages[:3] + ppages[page_prev:page_next] + ppages[-3:]
            separators = 2
    if int(current_page) > pages.num_pages:
        current_page=pages.num_pages
    context={
        "pages"                 : ppages,
        "num_pages"             : pages.num_pages,
        "current_page"          : pages.page(current_page),
        "current_page_idx"      : int(current_page),
        "separators"            : separators,
        "category"              : category,
        "coupons"               : pages.page(current_page).object_list,
        "num_coupons"           : pages.count,
        "total_coupon_count"    : category.get_coupon_count(),
        "coupon_categories"     : coupon_categories,
        "form_path"             : "/categories/{0}/".format(category.code),
    }
    set_meta_tags(category, context)
    if current_page > 1:
        context['canonical_url'] = "{0}pages/{1}/".format(category.og_url(), current_page)
    set_active_tab('category', context)

    if len(all_categories) != len(selected_categories):
        context["comma_categories"] = ShortenedURLComponent.objects.shorten_url_component(comma_categories).shortened_url

    return render_response("category.html", request, context)

def robots_txt(request):
    robots = """User-agent: *
Allow: /
Sitemap: http://s3.amazonaws.com/pushpenny/sitemap.xml
"""
    return HttpResponse(robots, content_type="text/plain")

def sitemap(request):
    return HttpResponseRedirect('http://s3.amazonaws.com/pushpenny/sitemap.xml')

@ensure_csrf_cookie
@cache_page(60 * 60 * 24)
def stores(request, page='#'):
    """List of stores, ordered by alphabet."""

    description = u"Stores List | {0}".format(base_description)
    category = request.GET.get('category', None)
    if page == '#':
        filters = {'name__regex': r'^[0-9]'}
    else:
        filters = {'name__istartswith': page}
    if category:
        merchant_ids = [c['merchant__id'] for c in Coupon.objects.filter(categories=category).values('merchant__id').annotate()]
        filters['id__in'] = merchant_ids
    filters['total_coupon_count__gt'] = 0
    stores = Merchant.objects.filter(**filters)
    context={
        "stores": stores,
        "categories": Category.objects.filter(parent__isnull=True, ref_id_source__isnull=True).order_by('name'),
        "category": int(category) if category else None,
        "page_description": description,
        "page_title": description,
        "pagination": AlphabeticalPagination(page),
        "og_title": "Stores List",
        "og_description": description,
        "og_image": icon_url,
        "og_url": "{0}/categories/".format(settings.BASE_URL_NO_APPENDED_SLASH),
    }
    set_active_tab('stores', context)
    return render_response("stores.html", request, context)

@ensure_csrf_cookie
def coupon_success_page(request, company_name, coupon_label, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
    except Coupon.DoesNotExist:
        coupon = Coupon.objects.filter(desc_slug=coupon_label).order_by('-id')
        if not coupon:
            raise Http404
        original_coupon_url = reverse('web.views.main.coupon_success_page', kwargs={'company_name': company_name,
                                                                                    'coupon_label': coupon_label,
                                                                                    'coupon_id': coupon[0].id})
        return HttpResponsePermanentRedirect(original_coupon_url)
    context={"coupon": coupon}
    return render_response("coupon_success_page.html",request, context)
