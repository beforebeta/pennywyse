import datetime
import os.path
from django.core.mail import send_mail
from celery import task
from core.management.commands.fmtcload import load
from tracking.management.commands.skimlinks import load_commissions
from tracking.utils import fetch_ad_costs, ADWORDS_EXPORT_FILE, FB_ADS_EXPORT_FILE

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
        

@task(max_retries=1)
def load_ad_costs():
    initial_timedelta = datetime.timedelta(minutes=5)
    try:
        adwords_modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(ADWORDS_EXPORT_FILE))
        adwords_changed = datetime.datetime.now() - adwords_modification_time > initial_timedelta
    except OSError:
        adwords_changed = fb_ads_changed = False
    try:
        fb_ads_modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(FB_ADS_EXPORT_FILE))
        fb_ads_changed = datetime.datetime.now() - fb_ads_modification_time > initial_timedelta
    except OSError:
        fb_ads_changed = False
    if adwords_changed or fb_ads_changed:
        fetch_ad_costs()