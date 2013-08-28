from optparse import make_option
from django.core.management import BaseCommand
from core.models import Coupon, Merchant


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
    print "Active Coupons: ", Coupon.active_objects.all().count()
    print "Inactive Coupons: ", (Coupon.objects.all().count() - Coupon.active_objects.all().count())
    print "Merchants: ", Merchant.objects.all().count()
