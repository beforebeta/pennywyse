from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.conf import settings
from subprocess import check_call
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        settings.AWS_DEFAULT_ACL = 'private'
        settings.AWS_REDUCED_REDUNDANCY = False

        db = settings.DATABASES['default']
        database = db['NAME']
        user = db['USER']
        password = db['PASSWORD']

        file_name = 'backups/{0}{1}.sql'.format(database,
                                                 datetime.datetime.now()
                                                 .strftime('%Y%m%d%H%M'))

        with open(file_name, 'wb') as backup:
            self.stdout.write('Grabbing database dump...\n\n')
            check_call(['mysqldump',
                        '--user=%s' % user,
                        '--password=%s' % password,
                        database], stdout=backup)

        with open(file_name) as backup:
            self.stdout.write('Uploading to S3...\n\n')
            default_storage.save(file_name, File(backup))

        self.stdout.write('Wrapping up...\n\n')
