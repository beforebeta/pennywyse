# from django.contrib import admin
from django.contrib.gis import admin
from core.models import Coupon, Category, Merchant, MerchantLocation

class CouponAdmin(admin.ModelAdmin):
    search_fields = ['description',"short_desc", "merchant__name"]

class MerchantAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']

admin.site.register(Coupon, CouponAdmin)
admin.site.register(Category)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(MerchantLocation, admin.GeoModelAdmin)