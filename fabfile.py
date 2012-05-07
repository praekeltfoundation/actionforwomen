from fabric.api import cd, prefix, run, sudo

def restart():
    sudo('/etc/init.d/nginx restart')
    sudo('supervisorctl reload')

def provision():
    sudo('apt-get update')
    sudo('apt-get install -y git-core puppet')
    run('rm -rf ~/mama')
    run('git clone https://github.com/praekelt/mama.git')
    with cd('mama'):
        sudo('puppet ./manifests/mama.pp --modulepath ./manifests/modules')
    with cd('/var/praekelt/mama'):
        with prefix('. ve/bin/activate'):
            sudo('./mama/manage.py syncdb', user="ubuntu")
            sudo('./mama/manage.py migrate', user="ubuntu")
            sudo('./mama/manage.py collectstatic', user="ubuntu")
    restart()
    run('rm -rf ~/mama')

def release():
    with cd('/var/praekelt/mama'):
        sudo('git pull origin master', user='ubuntu')
        with prefix('. ve/bin/activate'):
            sudo('./mama/manage.py syncdb', user="ubuntu")
            sudo('./mama/manage.py migrate', user="ubuntu")
            sudo('./mama/manage.py collectstatic', user="ubuntu")
    restart()
