from django.contrib import admin
from tracking.models import BannedIP, UntrackedUserAgent, Visitor, ClickTrack, RevenueVisitor, Commission,AcquisitionSource, AdCost, SearchQueryLog


class ClickTrackAdmin(admin.ModelAdmin):
    readonly_fields = ('coupon','merchant',)
    ordering = ['-date_added']
    list_display = ('acquisition_source', 'acquisition_medium','acquisition_campaign','acquisition_term','acquisition_content', 'target_url', 'source_url', 'merchant_domain')

class VisitorAdmin(admin.ModelAdmin):
    list_display = ('url', 'acquisition_source', 'acquisition_medium','acquisition_campaign','acquisition_term','acquisition_content')

class AdCostAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'campaign', 'ad', 'keyword', 'impression', 'social_impression', 'clicks', 'social_clicks', 
                    'costs', 'average_cpc', 'frequency', 'actions', 'unique_clicks', 'acquisition_source', 'acquisition_medium')

class SearchQueryLogAdmin(admin.ModelAdmin):
    list_display = ('query', 'found_coupons', 'found_merchants', 'visitor_link', 'redirected', 'date_added',)
    readonly_fields = ('visitor',)
    
    def visitor_link(self, obj):
        return '<a href="/admin/tracking/visitor/%s/" target="_blank">Visitor</a>' % obj.visitor_id
    
    visitor_link.allow_tags = True

admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
admin.site.register(Visitor, VisitorAdmin)
admin.site.register(RevenueVisitor)
admin.site.register(ClickTrack, ClickTrackAdmin)
admin.site.register(AcquisitionSource)
admin.site.register(Commission)
admin.site.register(AdCost, AdCostAdmin)
admin.site.register(SearchQueryLog, SearchQueryLogAdmin)