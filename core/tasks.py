from django.core.mail import send_mail
from celery import task
from core.management.commands.fmtcload import load


@task(max_retries=1)
def load_coupons():
    try:
        load()
    except Exception as e:
        load_coupons.retry(exc=e)