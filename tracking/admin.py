from django.contrib import admin
from tracking.models import BannedIP, UntrackedUserAgent, Visitor, ClickTrack, RevenueVisitor, Commission,AcquisitionSource


class ClickTrackAdmin(admin.ModelAdmin):
    readonly_fields = ('coupon','merchant',)
    ordering = ['-date_added']
    list_display = ('acquisition_source', 'acquisition_medium','acquisition_campaign','acquisition_term','acquisition_content', 'target_url', 'source_url', 'merchant_domain')

class VisitorAdmin(admin.ModelAdmin):
    list_display = ('url', 'acquisition_source', 'acquisition_medium','acquisition_campaign','acquisition_term','acquisition_content')

admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
admin.site.register(Visitor, VisitorAdmin)
admin.site.register(RevenueVisitor)
admin.site.register(ClickTrack, ClickTrackAdmin)
admin.site.register(AcquisitionSource)

admin.site.register(Commission)