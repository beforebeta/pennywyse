from django.contrib import admin
from core.models import Coupon, Merchant
from web.models import ShortenedURLComponent, CategorySection, TopCouponSection
from core.util import CustomModelAdmin

class CouponInline(admin.TabularInline):
    model = Coupon
    extra = 0
    fields = ('short_desc', 'merchant')
    readonly_fields = ('short_desc', 'merchant')

    def has_add_permission(self, request):
        return False


class FeaturedCouponInline(CouponInline):
    fk_name = 'featured_in'
    verbose_name_plural = 'Featured Coupons'


class PopularCouponInline(CouponInline):
    fk_name = 'popular_in'
    verbose_name_plural = 'Popular Coupons'


class StoreInline(admin.TabularInline):
    model = Merchant
    extra = 0
    fields = ('name',)
    readonly_fields = ('name',)
    verbose_name_plural = 'Stores'

    def has_add_permission(self, request):
        return False


class TopCouponSectionAdmin(CustomModelAdmin):
    inlines = [FeaturedCouponInline, PopularCouponInline, StoreInline]

class CategorySectionAdmin(CustomModelAdmin):
    pass

admin.site.register(ShortenedURLComponent)
admin.site.register(CategorySection, CategorySectionAdmin)
admin.site.register(TopCouponSection, TopCouponSectionAdmin)