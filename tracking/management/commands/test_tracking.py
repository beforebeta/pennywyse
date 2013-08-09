from optparse import make_option
from django.core.management import BaseCommand
import uuid
import requests
import time
from tracking.models import Visitor


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--run',
            action='store_true',
            dest='run',
            default=False,
            help='run'),
        )

    def handle(self, *args, **options):
        err = self.stderr
        out = self.stdout
        if options['run']:
            run()


def run():
    print "Testing tracking..."
    guid = uuid.uuid4().hex
    print "new =", guid

    medium = "campaign_1_no_visitor_%s" % guid
    print "Sending utm request with campaign set"
    url = "http://localhost:8002/coupons/amazon/?utm_source=%s&utm_medium=%s&utm_campaign=local+test" % (guid,medium)
    requests.get(url)
    v = Visitor.objects.get(acquisition_source=guid)
    print v.acquisition_source

    print "test 2 direct"
    url = "http://localhost:8002/coupons/amazon/"
    requests.get(url)
    v = Visitor.objects.get(id=6)
    print v.id
    print v.acquisition_source
