from django.contrib import admin
from tracking.models import BannedIP, UntrackedUserAgent, Visitor, ClickTrack

admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
admin.site.register(Visitor)
admin.site.register(ClickTrack)