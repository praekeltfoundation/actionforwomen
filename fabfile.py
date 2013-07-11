import os
from fabric.api import cd, sudo


def restart():
    sudo('/etc/init.d/nginx restart')
    sudo('supervisorctl reload')


def deploy():
    with cd('/var/praekelt/mama'):
        sudo('git pull', user='jmbo')
        sudo('ve/bin/python mama/manage.py syncdb --migrate --noinput',
             user='jmbo')
        sudo('ve/bin/python mama/manage.py collectstatic --noinput',
             user='jmbo')


def install_packages(force=False):
    with cd('/var/praekelt/mama'):
        sudo('ve/bin/pip install %s -r requirements.pip' % (
             '--update' if force else '',), user='jmbo')
