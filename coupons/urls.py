from django.conf.urls import patterns, include, url
from django.contrib import admin

# static
from django.conf import settings
from django.conf.urls.static import static

# cache
from django.views.decorators.cache import cache_page
cache_ttl = 24 * 60 * 60

# import views
from web.views import main

admin.autodiscover()

urlpatterns = patterns('',
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


    url(r'^categories/(?P<category_code>[A-z0-9-]+)/page/(?P<current_page>[\d]+)/$', cache_page(cache_ttl)(main.category)),
    url(r'^categories/(?P<category_code>[A-z0-9-]+)/$', cache_page(cache_ttl)(main.category)),
    url(r'^categories/$', cache_page(cache_ttl)(main.categories)),
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
    url(r'^emailD$', 'email_d')
)

urlpatterns += patterns('django.contrib.staticfiles.views',
    url(r'^static/(?P<path>.*)$', 'serve'),
    #url(r'^(?P<path>.*)$', 'serve'),
)

# (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
#         {'document_root': '/path/to/media'}),

#handler404 = 'web.views.main.index'

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


if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
