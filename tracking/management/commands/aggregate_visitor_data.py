from django.core.management import BaseCommand
from tracking.utils import aggregate_visitor_data

class Command(BaseCommand):

    def handle(self, *args, **options):
        aggregate_visitor_data()

