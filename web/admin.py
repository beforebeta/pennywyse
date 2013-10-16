from django.contrib import admin
from web.models import ShortenedURLComponent, NewCoupon, PopularCoupon, FeaturedCoupon, PopularSocialCoupon

admin.site.register(ShortenedURLComponent)
admin.site.register(FeaturedCoupon)
admin.site.register(NewCoupon)
admin.site.register(PopularCoupon)
admin.site.register(PopularSocialCoupon)