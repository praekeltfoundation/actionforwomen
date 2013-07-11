import os
from fabric.api import cd, sudo


def restart():
    sudo('/etc/init.d/nginx restart')
    sudo('supervisorctl reload')


def deploy():
    with cd('/var/praekelt/mama'):
        sudo('git pull', user='jmbo')
        sudo('pip install -r requirements.pip', user='jmbo')
        sudo('ve/bin/python mama/manage.py syncdb --migrate --noinput',
             user='jmbo')
        sudo('ve/bin/python mama/manage.py collectstatic --noinput',
             user='jmbo')
