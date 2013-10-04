from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'coupons.views.home', name='home'),
    # url(r'^coupons/', include('coupons.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

########################################################################################
# Web
########################################################################################
urlpatterns += patterns('web.views.main',
    url(r'^$', 'index'),
    url(r'^privacy-and-terms/$', 'privacy'),
    url(r'^coupons/(?P<company_name>[a-z0-9-_]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-z0-9-_]+)/(?P<company_id>[\d]+)/$', 'coupons_for_company'),

    url(r'^coupons/(?P<company_name>[a-z0-9-_]+)/page/(?P<current_page>[\d]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-z0-9-_]+)/(?P<company_id>[\d]+)/page/(?P<current_page>[\d]+)/$', 'coupons_for_company'),

    url(r'^coupons/(?P<company_name>[a-z0-9-_]+)/page/(?P<current_page>[\d]+)/categories/(?P<category_ids>sh_[a-fA-F0-9]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-z0-9-_]+)/(?P<company_id>[\d]+)/page/(?P<current_page>[\d]+)/categories/(?P<category_ids>sh_[a-fA-F0-9]+)/$', 'coupons_for_company'),

    url(r'^coupons/(?P<company_name>[a-z0-9-_]+)/(?P<coupon_label>[a-z0-9-]+)/(?P<coupon_id>[\d]+)/$', 'open_coupon'),
    #do not kill old links:
    url(r'^coupon/(?P<company_name>[a-z0-9-_]+)/(?P<coupon_label>[a-z0-9-]+)/(?P<coupon_id>[\d]+)/$', 'redirect_to_open_coupon'),


    url(r'^categories/(?P<category_code>[A-z0-9-]+)/page/(?P<current_page>[\d]+)/$', 'category'),
    url(r'^categories/(?P<category_code>[A-z0-9-]+)/$', 'category'),
    url(r'^categories/$', 'categories'),
    url(r'^stores/(?P<page>[A-Za-z]+)/$', 'stores'),
    url(r'^stores/$', 'stores'),

    url(r'^blog/', include('articles.urls')),
    url(r'^robots\.txt$', 'robots_txt'),
    url(r'^sitemap\.xml$', 'sitemap'),
)

urlpatterns += patterns('web.views.ajax',
    url(r'^a/subscribe/$', 'ajax_subscribe'),
)

urlpatterns += patterns('tracking.views',
    url(r'^a/clk/$', 'click_track'),
)

urlpatterns += patterns('web.views.search',
    url(r'^search/$', 'search')
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

urlpatterns += patterns('websvcs.views.subscriptions',
    url(r'^e/subscribe/$', 'email_subscribe')
)
