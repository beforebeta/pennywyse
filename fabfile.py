from fabric.api import *

def run_dev():
    with shell_env(DJANGO_SETTINGS_MODULE='coupons.settings_dev'):
        local('python manage.py runserver')

def run_staging():
    with shell_env(DJANGO_SETTINGS_MODULE='coupons.settings_staging'):
        local('gunicorn -t 300 coupons.wsgi')

def run_pro():
    with shell_env(DJANGO_SETTINGS_MODULE='coupons.settings_pro'):
        local('gunicorn coupons.wsgi')

def deploy_staging():
    local('heroku maintenance:on')
    branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
    local('git push heroku %s:master' % branch)
    local('heroku run python manage.py collectstatic --noinput')
    local('heroku maintenance:off')

def refresh_staging():
    local('heroku run python manage.py fmtcload --load')
