from django.conf.urls import patterns, include, url
from api.mobile_api import MobileResource

mobile_resource = MobileResource()

# API
urlpatterns = patterns('',
    url(r'^v3/deals', mobile_resource.deals_return_response),
    url(r'^v3/deal', mobile_resource.single_deal_return_response),
    url(r'^v3/localinfo', mobile_resource.localinfo_return_response),
)
