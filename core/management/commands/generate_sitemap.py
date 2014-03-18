from django.core.management.base import BaseCommand
from core.util.sitemap import generate_sitemap

class Command(BaseCommand):

    def handle(self, *args, **options):
        generate_sitemap()