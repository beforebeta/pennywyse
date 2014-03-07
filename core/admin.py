from django.contrib.gis import admin
from core.models import Coupon, Category, Merchant, MerchantLocation, CouponNetwork, CityPicture
from core.util import CustomModelAdmin

class CouponAdmin(CustomModelAdmin):
    search_fields = ['description',"short_desc", "merchant__name"]
    readonly_fields = ['ref_id', 'ref_id_source', 'merchant', 'merchant_location']
    exclude = ['related_deal']

class MerchantAdmin(CustomModelAdmin):
    search_fields = ['name', 'description']
    readonly_fields = ['ref_id', 'ref_id_source']

class CouponNetworkAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']

class CategoryAdmin(CustomModelAdmin):
    readonly_fields = ['ref_id', 'ref_id_source']
    search_fields = ('name', )

class CityPictureAdmin(admin.ModelAdmin):
    pass

class MerchantLocationAdmin(admin.GeoModelAdmin):
    readonly_fields = ['merchant',]

admin.site.register(Coupon, CouponAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(MerchantLocation, MerchantLocationAdmin)
admin.site.register(CouponNetwork, CouponNetworkAdmin)
admin.site.register(CityPicture, CityPictureAdmin)
