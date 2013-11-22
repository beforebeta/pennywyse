# from django.contrib import admin
from django.contrib.gis import admin
from core.models import Coupon, Category, Merchant, MerchantLocation,CouponNetwork

class CouponAdmin(admin.ModelAdmin):
    search_fields = ['description',"short_desc", "merchant__name"]
    readonly_fields = ['ref_id', 'ref_id_source']

class MerchantAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    readonly_fields = ['ref_id', 'ref_id_source']

class CouponNetworkAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']

class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['ref_id', 'ref_id_source']

admin.site.register(Coupon, CouponAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(MerchantLocation, admin.GeoModelAdmin)
admin.site.register(CouponNetwork, CouponNetworkAdmin)