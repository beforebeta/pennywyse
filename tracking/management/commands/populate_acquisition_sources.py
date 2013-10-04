import sys
from itertools import chain, imap
from optparse import make_option
from urllib2 import urlopen, HTTPError, URLError

from django.db import DatabaseError
from django.core.management.base import BaseCommand, CommandError

from tracking.models import AcquisitionSource


class Command(BaseCommand):
    args = '<input file>'

    option_list = BaseCommand.option_list + (
        make_option('-f', '--delimiter', dest='delim', default='\t',
                    help='Field delimiter'),
        make_option('-d', '--delete', action='store_true', dest='delete',
                    default=False, help='Delete all records first'),
    )

    def handle(self, *args, **options):
        if args:
            lines = file(args[0])
        else:
            lines = iter(sys.stdin)

        if options['delete']:
            print >> sys.stderr, 'Deleting all existing records'
            AcquisitionSource.objects.all().delete()

        verbose = int(options.get('verbosity', '1'))
        delim = options['delim']

        for line in lines:
            print line
            line = line.strip()
            if not line:
                continue

            try:
                name, tag, logo_url = line.split(delim, 2)
            except ValueError:
                print >> sys.stderr, 'Malformed line {0!r}'.format(line)
                continue

            try:
                urlopen(logo_url)
            except (ValueError, URLError, HTTPError):
                print >> sys.stderr, 'Failed to download {0}'.format(
                    logo_url)
                continue

            try:
                src = AcquisitionSource(tag=tag, logo_url=logo_url)
                src.save()
            except DatabaseError:
                print >> sys.stderr, 'Failed to insert record {0!r}'.format(src)
                continue

            if verbose:
                print 'Inserted {0!r}'.format(src)
