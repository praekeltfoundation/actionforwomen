from fabric.api import *
env.sudo_user = 'jmbo'
env.path = '/var/praekelt/mama'
env.shell = '/bin/bash -c'


def qa(ssh_user=None):
    if not ssh_user:
        print 'You must provide your login username.'
        print 'format: fab <env>:<username> <command>'
        print ' e.g fab qa:miltontony push'
        raise RuntimeError('Username required')

    env.hosts = ['%s@qa-mama.za.prk-host.net' % ssh_user]
    env.is_prod = False


def prod(ssh_user=None):
    if not ssh_user:
        print 'You must provide your login username.'
        print 'format: fab <env>:<username> <command>'
        print ' e.g fab prod:ubuntu push'
        raise RuntimeError('Username required')

    env.hosts = ['%s@prd-mama.za.prk-host.net' % ssh_user]
    env.is_prod = True



def restart():
    sudo('/etc/init.d/nginx restart')
    sudo('supervisorctl reload')


def push():
    with cd(env.path):
        sudo('git pull', user=env.sudo_user)


def migrate():
    with cd(env.path):
        sudo('ve/bin/python mama/manage.py syncdb --migrate --noinput',
             user=env.sudo_user)


def static():
    with cd(env.path):
        sudo('ve/bin/python mama/manage.py collectstatic --noinput',
             user=env.sudo_user)


def deploy():
    with cd(env.path):
        push()
        migrate()
        static()


def install_packages(force=False):
    with cd(env.path):
        sudo('ve/bin/pip install %s -r requirements.pip' % (
             '--upgrade' if force else '',), user=env.sudo_user)


def release():
    with cd(env.path):
        push()
        install_packages()
        migrate()
        static()

    sudo('sudo supervisorctl restart '
         'mama_mobi.gunicorn:mama_mobi.gunicorn_1')

    numprocs = 4 if env.is_prod else 1

    for i in range(1, numprocs + 1):
        sudo('sudo supervisorctl restart '
             'mama_mxit.gunicorn:mama_mxit.gunicorn_%s' % str(i))
    for i in range(1, numprocs + 1):
        sudo('sudo supervisorctl restart '
             'mama_vlive.gunicorn:mama_vlive.gunicorn_%s' % str(i))
    sudo('sudo supervisorctl restart mama.celery')
