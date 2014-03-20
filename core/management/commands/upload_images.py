from django.core.management.base import BaseCommand
from core.util import upload_images_to_s3

class Command(BaseCommand):
    def handle(self, *args, **options):
        upload_images_to_s3()
    
    
