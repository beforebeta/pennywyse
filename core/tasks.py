from celery import task
from core.management.commands.fmtload import load

@task()
def load_coupons():
    load()