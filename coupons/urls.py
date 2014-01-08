from django.conf.urls import patterns, include, url
from django.contrib import admin
from api.mobile_api import MobileResource
admin.autodiscover()
mobile_resource = MobileResource()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

########################################################################################
# Web
########################################################################################
urlpatterns += patterns('web.views.main',
    url(r'^$', 'index'),
    url(r'^page/(?P<current_page>[\d]+)/$', 'index'),
    url(r'^privacy-and-terms/$', 'privacy'),
    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/(?P<company_id>[\d]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/(?P<coupon_label>[a-z0-9-_]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/page/(?P<current_page>[\d]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/(?P<company_id>[\d]+)/page/(?P<current_page>[\d]+)/$', 'coupons_for_company'),

    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/page/(?P<current_page>[\d]+)/categories/(?P<category_ids>sh_[a-fA-F0-9]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/(?P<company_id>[\d]+)/page/(?P<current_page>[\d]+)/categories/(?P<category_ids>sh_[a-fA-F0-9]+)/$', 'coupons_for_company'),

    # do not kill old links:
    url(r'^coupon/(?P<company_name>[a-zA-Z0-9-_]+)/(?P<coupon_label>[a-z0-9-_]+)/(?P<coupon_id>[\d]+)/$', 'redirect_to_open_coupon'),
    url(r'^coupons/(?P<company_name>[a-zA-Z0-9-_]+)/(?P<coupon_label>[a-zA-Z0-9-_]+)/(?P<coupon_id>[\d]+)/ty/$', 'coupon_success_page'),

    url(r'^categories/(?P<category_code>[a-zA-Z0-9-]+)/page/(?P<current_page>[\d]+)/$', 'category'),
    url(r'^categories/(?P<category_code>[a-zA-Z0-9-]+)/$', 'category'),
    url(r'^categories/$', 'categories'),
    url(r'^stores/(?P<page>[#a-zA-Z]+)/$', 'stores'),
    url(r'^stores/$', 'stores'),
    url(r'^e/subscribe/$', 'email_subscribe'),
    url(r'^o/(?P<coupon_id>[\d]+)/$', 'open_coupon'),

# /blog/ is being served by WordPress
#    url(r'^blog/', include('articles.urls')),
    url(r'^robots\.txt$', 'robots_txt'),
    url(r'^sitemap\.xml$', 'sitemap'),
)

urlpatterns += patterns('tracking.views',
    url(r'^a/clk/$', 'click_track'),
)

urlpatterns += patterns('web.views.search',
    url(r'^search/$', 'search'),
    url(r'^search/page/(?P<current_page>[\d]+)/$', 'search')
)

urlpatterns += patterns('web.views.email',
    url(r'^emailA$', 'email_a'),
    url(r'^emailB$', 'email_b'),
    url(r'^emailC$', 'email_c'),
    url(r'^emailD$', 'email_d'),
)

handler404 = 'web.views.main.index'

########################################################################################
# WebSvcs
########################################################################################

urlpatterns += patterns('websvcs.views.image',
    url(r'^s/image/(?P<image_url>.+)/(?P<height>[\d]+)x(?P<width>[\d]+)/$', 'image_resize'),
    url(r'^s/image/(?P<image_url>http.+)/$', 'image')
)
########################################################################################
# API
########################################################################################

urlpatterns += patterns('api.views',
    url(r'^v2/deals', 'deals'),
    url(r'^v2/localinfo', 'localinfo'),
)

urlpatterns += patterns('',
    url(r'^v3/deals', mobile_resource.deals_return_response),
    url(r'^v3/localinfo', mobile_resource.localinfo_return_response),
)
