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
    url(r'^coupons/(?P<company_name>[a-z0-9-]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-z0-9-]+)/(?P<company_id>[\d]+)/$', 'coupons_for_company'),

    url(r'^coupons/(?P<company_name>[a-z0-9-]+)/page/(?P<current_page>[\d]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-z0-9-]+)/(?P<company_id>[\d]+)/page/(?P<current_page>[\d]+)/$', 'coupons_for_company'),

    url(r'^coupons/(?P<company_name>[a-z0-9-]+)/page/(?P<current_page>[\d]+)/categories/(?P<category_ids>sh_[a-fA-F0-9]+)/$', 'coupons_for_company'),
    url(r'^coupons/(?P<company_name>[a-z0-9-]+)/(?P<company_id>[\d]+)/page/(?P<current_page>[\d]+)/categories/(?P<category_ids>sh_[a-fA-F0-9]+)/$', 'coupons_for_company'),

    url(r'^coupon/(?P<company_name>[a-z0-9-]+)/(?P<coupon_label>[a-z0-9-]+)/(?P<coupon_id>[\d]+)/$', 'open_coupon'),


    url(r'^categories/(?P<category_name>[A-z0-9]+)/page/(?P<current_page>[\d]+)/$', 'category'),
    url(r'^categories/(?P<category_name>[A-z0-9]+)/$', 'category'),
    url(r'^categories/$', 'categories'),
)

urlpatterns += patterns('web.views.ajax',
    url(r'^a/subscribe/$', 'ajax_subscribe')
)

urlpatterns += patterns('web.views.search',
    url(r'^search/$', 'search')
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
