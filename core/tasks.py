from django.core.mail import send_mail
from celery import task
from core.management.commands.fmtcload import load
from tracking.management.commands.skimlinks import load_commissions

@task(max_retries=1)
def load_coupons():
    try:
        load()
    except Exception as e:
        load_coupons.retry(exc=e)
        
@task(max_retries=1)
def load_skimlinks_commissions():
    try:
        load_commissions()
    except Exception as e:
        load_skimlinks_commissions.retry(exc=e)