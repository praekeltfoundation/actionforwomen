====
Mama
====

|mama-ci|_

.. |mama-ci| image:: https://magnum.travis-ci.com/praekelt/mama.png?token=hvdqE3zapc2LPyKs2zQC&branch=develop
.. _mama-ci: https://magnum.travis-ci.com/praekelt/mama

Getting Started
===============

Create and install environment packages by executing the following commands::

    $ virtualenv ve
    $ . ve/bin/activate
    $ pip install -r requirements.pip


Notes
=====

Mama uses Haystack for search. When deploying remember to add a cronjob periodically updating the search index, i.e::
  
    0 0 * * * cd /var/praekelt/mama && . ve/bin/activate && ./mama/manage.py update_index && deactivate


Deploying
=========

Remote Host Fabric Deploy
-------------------------

Provision
+++++++++
To provision a new instance on a remote host run the following command using a user with superuser privileges on the remote host:: 
    
    $ fab -H hostname:port -u user provision

After the provision access by hitting the hostname in your browser.

Release
+++++++
To release new code on an existing instance run the following command using a user with superuser privileges on the remote host:: 
    
    $ fab -H hostname:port -u user release

This will pull the latest code from the ``master`` branch and restart the instance.

Restart
+++++++
To restart a remote instance previously provisioned run the following command using a user with superuser privileges on the remote host:: 
    
    $ fab -H hostname:port -u user restart

This will restart `Nginx <http://wiki.nginx.org/Main>`_ and reload `Supervisor <http://supervisord.org/>`_, thus restarting the instance.

Local Vagrant Deploy
--------------------
Deploy a local Vagrant instance like so::
    
    you@host$ git clone git@github.com:praekelt/mama.git
    you@host$ cd mama
    you@host$ vagrant up
    you@host$ vagrant ssh
    vagrant@lucid32$ sudo -i
    vagrant@lucid32$ su ubuntu
    ubuntu@lucid32$ cd /var/praekelt/mama
    ubuntu@lucid32$ . ve/bin/activate
    (ve)ubuntu@lucid32$ ./mama/manage.py syncdb
    (ve)ubuntu@lucid32$ ./mama/manage.py migrate
    (ve)ubuntu@lucid32$ ./mama/manage.py collectstatic
    (ve)ubuntu@lucid32$ exit
    root@lucid32$ /etc/init.d/nginx restart
    root@lucid32$ supervisorctl reload

Then access the instance on `localhost port 4567 <http://localhost:4567>`_.

