import datetime
import os.path
from celery import task
from core.util.sitemap import generate_sitemap
from core.management.commands.fmtcload import load
from core.management.commands.sqootload import (refresh_sqoot_data, clean_out_sqoot_data,
                                                validate_sqoot_data, dedup_sqoot_data_hard, )
from tracking.management.commands.skimlinks import load_commissions
from tracking.utils import ADWORDS_EXPORT_FILE, FB_ADS_EXPORT_FILE, fetch_ad_costs, aggregate_visitor_data

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


@task(max_retries=0)
def run_sqootload_shortcycle():
    refresh_sqoot_data()
    clean_out_sqoot_data()
    validate_sqoot_data()
    dedup_sqoot_data_hard()


@task(max_retries=1)
def process_visitor_data():
    try:
        aggregate_visitor_data()
    except Exception as e:
        process_visitor_data.retry(exc=e)


@task(max_retries=1)
def build_sitemap():
    try:
        generate_sitemap()
    except Exception as e:
        build_sitemap.retry(exc=e)