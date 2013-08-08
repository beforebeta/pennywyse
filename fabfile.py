from fabric.api import *

def dev():
    config.fab_hosts = ['pennywyse.local']
    config.target_dir = '/Users/jacob/Sites/pennywyse'
    config.target = 'dev'
    config.migrate_db = True

def production():
    config.fab_hosts = ['pennywyse.com']
    config.target_dir = '/home/sam/'
    config.target = 'pro'
    config.migrate_db = True


@task
def start():
    local('source ../pennyenv/bin/activate')

#def deploy():
