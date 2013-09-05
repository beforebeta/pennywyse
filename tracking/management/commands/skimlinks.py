from optparse import make_option
from django.core.management import BaseCommand
import uuid
import requests
import time
from tracking.commission.skimlinks import ReportingAPI
from tracking.models import Visitor, Commission
import json

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--load_commissions',
            action='store_true',
            dest='load_commissions',
            default=False,
            help='load_commissions'),
        )

    def handle(self, *args, **options):
        err = self.stderr
        out = self.stdout
        if options['load_commissions']:
            load_commissions()


def load_commissions():
    r = ReportingAPI()
    commissions = r.get_commissions()
    # commissions = json.loads(open("comm.js","r").read())
    # print json.dumps(commissions["skimlinksAccount"]["commissions"]["commission"], indent=4)
    Commission.objects.create_from_skimlinks_commissions(commissions)
    print "Commissions Count", Commission.objects.all().count()


