# Globally set exec paths and user.
Exec {
    path => ["/bin", "/usr/bin", "/usr/local/bin"],
    user => 'ubuntu',
}

# Update package index.
exec { "update_apt":
    command => "apt-get update",
    user => "root",
}

# Install required packages.
package { [
    "git-core",
    "libpq-dev",
    "libxml2-dev",
    "libxslt-dev",
    "nginx",
    "postgresql",
    "python-dev",
    "python-virtualenv",
    "supervisor",
    ]:
    ensure => latest,
    subscribe => Exec['update_apt'];
}

# Ensure Ubuntu user exists
user { "ubuntu":
    ensure => "present",
    home => "/home/ubuntu",
    shell => "/bin/bash"
}

# Create the deployment directory
file { "/var/praekelt/":
    ensure => "directory",
    owner => "ubuntu",
    subscribe => User["ubuntu"]
}

# Clone and update repo.
exec { "clone_repo":
    command => "git clone git@github.com:praekelt/mama.git mama",
    cwd => "/var/praekelt",
    unless => "test -d /var/praekelt/mama",
    subscribe => [
        Package['git-core'],
        File['/var/praekelt/'],
    ]
}

exec { "update_repo":
    command => "git pull origin",
    cwd => "/var/praekelt/mama",
    subscribe => [
        Exec['clone_repo'],
    ]
}

# Create virtualenv.
exec { 'create_virtualenv':
    command => 'virtualenv --no-site-packages ve',
    cwd => '/var/praekelt/mama',
    unless => 'test -d /var/praekelt/mama/ve',
    subscribe => [
        Package['libpq-dev'],
        Package['libxml2-dev'],
        Package['libxslt-dev'],
        Package['python-dev'],
        Package['python-virtualenv'],
#        Package['solr-tomcat'],
        Exec['clone_repo'],
    ]
}

# Install python packages.
exec { 'install_packages':
    command => '/bin/sh -c ". ve/bin/activate && pip install -r requirements.pip && deactivate"',
    cwd => '/var/praekelt/mama',
    subscribe => [
        Exec['create_virtualenv'],
        Exec['update_repo'],
    ]
}

# Manage Nginx symlinks.
file { "/etc/nginx/sites-enabled/mama.conf":
    ensure => symlink,
    target => "/var/praekelt/mama/config/nginx.conf",
    require => [
        Exec['update_repo'],
        Package['nginx'],
    ]
}

file { "/etc/nginx/sites-enabled/default":
    ensure => absent,
    subscribe => [
        Exec['update_repo'],
        Package['nginx'],
    ]
}

# Manage supervisord symlinks.
file { "/etc/supervisor/conf.d/mama.conf":
    ensure => symlink,
    target => "/var/praekelt/mama/config/supervisord.conf",
    subscribe => [
        Exec['update_repo'],
        Package['supervisor']
    ]
}

# Create Postgres role and database.
postgres::role { "mama":
    password => mama,
    ensure => present,
    subscribe => [
        Exec['update_repo'],
        Package['postgresql']
    ]
}

postgres::database { "mama":
    owner => mama,
    ensure => present,
    template => "template0",
    subscribe => [
        Exec['update_repo'],
        Package['postgresql']
    ]
}

file {
    "/home/ubuntu/":
        ensure => 'directory',
        owner => 'ubuntu',
        require => User['ubuntu'];
    "ubuntu_ssh_dir":
        path => '/home/ubuntu/.ssh',
        ensure => directory,
        owner => ubuntu,
        group => ubuntu,
        require => User['ubuntu'];
    "ubuntu_id_rsa":
        path => '/home/ubuntu/.ssh/id_rsa',
        ensure => present,
        owner => ubuntu,
        group => ubuntu,
        mode => 0600,
        require => [ User['ubuntu'], File['ubuntu_ssh_dir'], ],
        source => 'puppet:///modules/base/id_rsa';
    "ubuntu_id_rsa.pub":
        path => '/home/ubuntu/.ssh/id_rsa.pub',
        ensure => present,
        owner => ubuntu,
        group => ubuntu,
        mode => 0644,
        require => [ User['ubuntu'], File['ubuntu_ssh_dir'], ],
        source => 'puppet:///modules/base/id_rsa.pub';
}
