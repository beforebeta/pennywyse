from django.contrib import admin
from tracking.models import BannedIP, UntrackedUserAgent, Visitor, ClickTrack, RevenueVisitor

class ClickTrackAdmin(admin.ModelAdmin):
    readonly_fields = ('coupon','merchant',)
    ordering = ['-date_added']

class VisitorAdmin(admin.ModelAdmin):
    fields = ('url', 'acquisition_source', 'acquisition_medium','acquisition_campaign','acquisition_term','acquisition_content')

admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
admin.site.register(Visitor, VisitorAdmin)
admin.site.register(RevenueVisitor)
admin.site.register(ClickTrack, ClickTrackAdmin)