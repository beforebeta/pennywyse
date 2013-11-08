from django.core.management import BaseCommand
from tracking.utils import fetch_ad_costs,ADWORDS_EXPORT_FILE,FB_ADS_EXPORT_FILE

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        fetch_ad_costs()
        