from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.conf import settings
from subprocess import check_output
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        settings.AWS_DEFAULT_ACL = 'private'

        file_name = 'backups/coupons{0}.sql'.format(datetime.datetime.now().strftime('%Y%m%d%H%M'))

        self.stdout.write('Grabbing database dump...\n\n')
        sql_string = check_output(['mysqldump', '-u', 'dbuser', '--password=dbuser', 'coupons'])

        self.stdout.write('Uploading to S3...\n\n')
        default_storage.save(file_name, ContentFile(sql_string))


        self.stdout.write('Wrapping up...\n\n')
