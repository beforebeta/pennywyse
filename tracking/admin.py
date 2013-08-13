from django.contrib import admin
from tracking.models import BannedIP, UntrackedUserAgent, Visitor, ClickTrack, RevenueVisitor


class ClickTrackAdmin(admin.ModelAdmin):
    readonly_fields = ('coupon','merchant',)
    ordering = ['-date_added']

admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
admin.site.register(Visitor)
admin.site.register(RevenueVisitor)
admin.site.register(ClickTrack, ClickTrackAdmin)