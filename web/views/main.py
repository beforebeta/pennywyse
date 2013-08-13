# Create your views here.
import random
from django.contrib.sites.models import get_current_site
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import ensure_csrf_cookie
from core.models import Category, Coupon, Merchant
from core.util import encode_uri_component, print_stack_trace
from web.models import FeaturedCoupon, NewCoupon, PopularCoupon, ShortenedURLComponent
import math
from django.core.paginator import Paginator

def build_base_context(request, context):
    context["pop_companies"] = Merchant.objects.get_popular_companies(21)
    context["coupons_path"] = "/"
    context["categories_path"] = "/categories"
    context["companies_path"] = "/companies"
    try:
        context["visitor"] = request.visitor
    except:
        print_stack_trace()

def render_response(template_file, request, context={}):
    build_base_context(request, context)
    return render_to_response(template_file, context, context_instance=RequestContext(request))

def set_active_tab(active_tab, context):
    if active_tab == "category":
      context['category_tab_class'] = 'active'
      context['company_tab_class'] = ''
      context['coupon_tab_class'] = ''
    elif active_tab == "company":
      context['company_tab_class'] = 'active'
      context['category_tab_class'] = ''
      context['coupon_tab_class'] = ''
    else:
      context['coupon_tab_class'] = 'active'
      context['company_tab_class'] = ''
      context['category_tab_class'] = ''

@ensure_csrf_cookie
def index(request):
    context = {}
    context["featured_coupons"] = list(FeaturedCoupon.objects.all()[:10])
    random.shuffle(context["featured_coupons"])
    context["new_coupons"] = [Coupon.objects.get(id=nc.coupon_id) for nc in NewCoupon.objects.all().order_by("-date_added")[:8]]
    context["pop_coupons"] = [Coupon.objects.get(id=pc.coupon_id) for pc in PopularCoupon.objects.all().order_by("-date_added")[:8]]
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
        merchant = Merchant.objects.get(name_slug= slugify(company_name))
    else:
        merchant = Merchant.objects.get(id=company_id)
    selected_categories = ""
    if selected_cat_ids == -1:
        selected_categories = ",".join(set([str(x["categories__id"]) for x in merchant.coupon_set.all().values("categories__id") if x["categories__id"]]))
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
                                    merchant.get_coupons().filter(
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
        "total_coupon_count"    : merchant.coupon_count
    }
    context["coupon_categories"] = coupon_categories

    if len(all_categories) != len(selected_categories):
        context["comma_categories"] = ShortenedURLComponent.objects.shorten_url_component(comma_categories).shortened_url

    return render_response("company.html", request, context)

@ensure_csrf_cookie
def open_coupon(request, company_name, coupon_label, coupon_id):
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
        "coupon"        : Coupon.objects.get(id=coupon_id),
        "logo_url"      : logo_url,
        "back_url"      : back_url,
        "path"          : encode_uri_component("%s://%s%s" % ("http", "www.pennywyse.com", request.path))
    }
    print context["path"]
    return render_response("open_coupon.html",request, context)

@ensure_csrf_cookie
def privacy(request):
    return render_response("privacy.html", request, {})

@ensure_csrf_cookie
def categories(request):
    context={
        "categories"        : sorted(Category.objects.filter(parent=None), key=lambda category: category.name)
    }
    set_active_tab('category', context)
    return render_response("categories.html", request, context)

@ensure_csrf_cookie
def category(request, category_code, current_page=1, category_ids=-1):
    current_page = int(current_page)
    category = Category.objects.get(code=category_code)

    if category_ids == -1:
        all_categories = [str(x["categories__id"]) for x in category.coupon_set.all().values("categories__id") if x["categories__id"]]
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

    pages = Paginator(
                        list(
                                set(
                                    category.get_coupons().filter(
                                        Q(categories__id__in=selected_categories) |
                                        Q(categories__id__isnull=True)
                                    )
                                )
                        ), 10)
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
        "form_path"             : "/categories/{0}/".format(category.code)
    }
    set_active_tab('category', context)

    if len(all_categories) != len(selected_categories):
        context["comma_categories"] = ShortenedURLComponent.objects.shorten_url_component(comma_categories).shortened_url

    return render_response("category.html", request, context)
