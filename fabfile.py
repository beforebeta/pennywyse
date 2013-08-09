from fabric.api import *

def run_dev():
    with shell_env(DJANGO_SETTINGS_MODULE='coupons.settings_dev'):
        local('python manage.py runserver')

def run_staging():
    with shell_env(DJANGO_SETTINGS_MODULE='coupons.settings_staging'):
        local('gunicorn coupons.wsgi')

def run_pro():
    with shell_env(DJANGO_SETTINGS_MODULE='coupons.settings_pro'):
        local('python manage.py runserver')

def deploy_staging():
    local('git push heroku staging:master')
