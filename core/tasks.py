from celery import task
from core.management.commands.fmtcload import load

@task()
def load_coupons():
    load()