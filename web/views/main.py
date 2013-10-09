# Create your views here.
import math, random, re
import string
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from core.models import Category, Coupon, Merchant, base_description, icon_url
from core.util import encode_uri_component, print_stack_trace
from core.util.pagination import AlphabeticalPagination
from tracking.views import log_click_track
from web.models import FeaturedCoupon, NewCoupon, PopularCoupon, ShortenedURLComponent
from django.core.paginator import Paginator

def build_base_context(request, context):
    context["pop_companies"] = Merchant.objects.get_popular_companies(21)
    context["coupons_path"] = "/"
    context["categories_path"] = "/categories"
    context["companies_path"] = "/companies"
    context["blog_path"] = "/blog"
    try:
        context["visitor"] = request.visitor
    except:
        try:
            if '/favicon.ico' in request.path:
                pass
            else:
                print "Error happened at ", request.path
                print_stack_trace()
        except:
            pass

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
def index(request):
    context = {
      "page_title" : base_description,
      "page_description" : base_description,
      "og_title" : "PennyWyse",
      "og_description" : "Hand Verified Coupon Codes",
      "og_image" : icon_url,
      "og_url" : settings.BASE_URL_NO_APPENDED_SLASH,
      "featured_coupons" : list(FeaturedCoupon.objects.all()),
      "new_coupons" : [Coupon.objects.get(id=nc.coupon_id) for nc in NewCoupon.objects.all().order_by("-date_added")[:8]],
      "pop_coupons" : [Coupon.objects.get(id=pc.coupon_id) for pc in PopularCoupon.objects.all().order_by("-date_added")[:8]],
    }
    random.shuffle(context['featured_coupons'])

    set_canonical_url(request, context)
    set_active_tab('coupon', context)
    return render_response("index.html", request, context)

def _search(itm,lst,f):
    for l in lst:
        if f(itm,l):
            return True
    return False

@ensure_csrf_cookie
def coupons_for_company(request, company_name, company_id=-1, current_page=1, category_ids=-1):
    selected_cat_ids = category_ids
    if selected_cat_ids != -1:
        selected_cat_ids = ShortenedURLComponent.objects.get_original_url(selected_cat_ids)
    if request.POST:
        selected_cat_ids = []
        for param in request.POST:
            try:
                selected_cat_ids.append(str(int(param)))
            except:
                pass
        selected_cat_ids=",".join(selected_cat_ids)
    merchant=None
    current_page = int(current_page)
    if company_id == -1:
        # merchant = Merchant.objects.get(name_slug= slugify(company_name)) -> this will error out if two merchants have the same slug
        merchant = Merchant.objects.filter(name_slug= slugify(company_name)).order_by("-id")[0]
    else:
        merchant = Merchant.objects.get(id=company_id)
    selected_categories = ""
    if selected_cat_ids == -1:
        selected_categories = ",".join(set([str(x["categories__id"]) for x in merchant.get_active_coupons().values("categories__id") if x["categories__id"]]))
    else:
        selected_categories = selected_cat_ids
    comma_categories = selected_categories
    try:
        selected_categories=[int(s) for s in selected_categories.split(",") if s]
    except:
        selected_categories=[]
#        selected_categories = list(set([int(x["categories__id"]) for x in merchant.coupon_set.all().values("categories__id") if x["categories__id"]]))
    all_categories = merchant.get_coupon_categories()
    coupon_categories = []
    for category in all_categories:
        coupon_categories.append({
            "category"  : category,
            "active"    : _search(category, selected_categories, lambda a,b:a.id==b)
        })

    pages = Paginator(
                        list(
                                set(
                                    merchant.get_active_coupons().filter(
                                        Q(categories__id__in=selected_categories) |
                                        Q(categories__id__isnull=True)
                                    )
                                )
                        ), 10)
    if current_page > pages.num_pages:
        current_page=pages.num_pages
    context={
        "merchant"              : merchant,
        "pages"                 : range(1, pages.num_pages+1),
        "current_page"          : int(current_page),
        "coupons"               : pages.page(current_page).object_list,
        "num_coupons"           : pages.count,
        "total_coupon_count"    : merchant.coupon_count,
        "coupon_categories"     : coupon_categories,
    }
    set_meta_tags(merchant, context)
    if current_page > 1:
      context['canonical_url'] = "{0}pages/{1}/".format(merchant.og_url(), current_page)

    if len(all_categories) != len(selected_categories):
        context["comma_categories"] = ShortenedURLComponent.objects.shorten_url_component(comma_categories).shortened_url

    return render_response("company.html", request, context)

@ensure_csrf_cookie
def redirect_to_open_coupon(request, company_name, coupon_label, coupon_id):
  return HttpResponsePermanentRedirect('{0}/coupons/{1}/{2}/{3}'.format(settings.BASE_URL_NO_APPENDED_SLASH, company_name, coupon_label, coupon_id))

@ensure_csrf_cookie
def open_coupon(request, company_name, coupon_label, coupon_id):
    log_click_track(request)

    coupon = Coupon.objects.get(id=coupon_id)
    if coupon.merchant.redirect:
      return HttpResponseRedirect(coupon.merchant.link)

    logo_url = "/"
    back_url = "/"
    try:
        logo_url = request.META["HTTP_REFERER"]
        back_url = logo_url
        if "localhost" not in logo_url and "pennywyse.com" not in logo_url:
            logo_url="/"
    except:
        pass

    context={
        "coupon"        : coupon,
        "logo_url"      : logo_url,
        "back_url"      : back_url,
        "path"          : encode_uri_component("%s://%s%s" % ("http", "www.pennywyse.com", request.path)),
    }
    set_meta_tags(coupon, context)

    return render_response("open_coupon.html",request, context)

@ensure_csrf_cookie
def privacy(request):
    return render_response("privacy.html", request, {})

@ensure_csrf_cookie
def categories(request):
    description = "Coupon Categories | {0}".format(base_description)
    context={
        "categories"        : sorted(Category.objects.filter(parent=None), key=lambda category: category.name),
        "page_description" : description,
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
def category(request, category_code, current_page=1, category_ids=-1):
    current_page = int(current_page)
    category = Category.objects.get(code=category_code)

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

    if current_page > pages.num_pages:
        current_page=pages.num_pages
    context={
        "category"              : category,
        "pages"                 : range(1, pages.num_pages+1),
        "current_page"          : int(current_page),
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
Sitemap: http://s3.amazonaws.com/pennywyse/sitemap.xml
"""
  return HttpResponse(robots, content_type="text/plain")

def sitemap(request):
  return HttpResponseRedirect('http://s3.amazonaws.com/pennywyse/sitemap.xml')

@ensure_csrf_cookie
def stores(request, page='A'):
    """List of stores, ordered by alphabet."""
    
    description = u"Stores List | {0}".format(base_description)
    category = request.GET.get('category', None)
    filters = {'name__istartswith': page}
    if category:
        merchant_ids = [c['merchant__id'] for c in Coupon.objects.filter(categories=category).values('merchant__id').annotate()]
        filters['id__in'] = merchant_ids
    stores = Merchant.objects.filter(**filters)
    context={
        "stores": stores,
        "categories": Category.objects.filter(parent=None).order_by('name'),
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