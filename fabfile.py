from fabric.api import *

env.path = '/var/praekelt/actionforwomen'
env.ve = '/var/praekelt/python'
env.sudo_user = 'ubuntu'
env.shell = '/bin/bash -c'


def qa(ssh_user=None):
    if not ssh_user:
        print 'You must provide your login username.'
        print 'format: fab <env>:<username> <command>'
        print ' e.g fab qa:miltontony deploy'
        raise RuntimeError('Username required')

    env.hosts = ['%s@qa.a4w.praekeltfoundation.org' % ssh_user]


def prod(ssh_user=None):
    if not ssh_user:
        print 'You must provide your login username.'
        print 'format: fab <env>:<username> <command>'
        print ' e.g fab prod:ubuntu push'
        raise RuntimeError('Username required')

    env.hosts = ['%s@a4w.ca' % ssh_user]


def push():
    with cd(env.path):
        sudo('git pull', user=env.sudo_user)


def static():
    with cd(env.path):
        sudo(
            '%(ve)s/bin/python manage.py collectstatic --noinput' % env,
            user=env.sudo_user)


def migrate(app=''):
    with cd(env.path):
        env.app = app
        sudo(
            '%(ve)s/bin/python manage.py migrate %(app)s' % env,
            user=env.sudo_user)


def pip():
    with cd(env.path):
        sudo(
            '%(ve)s/bin/pip install -r requirements.txt' % env,
            user='root')


def deploy():
    with cd(env.path):
        push()
        pip()
        static()
        migrate()
        sudo('supervisorctl restart actionforwomen_mobi', user='root')
        sudo('supervisorctl restart actionforwomen_mobi_fr', user='root')
        sudo('supervisorctl restart actionforwomen_celery', user='root')
