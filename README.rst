================
Action for Women
================

Getting Started
===============

Prerequisites
-------------

Make sure the following is already running on your server:

- Postgresql
- ElasticSearch

Installation
------------

Create and install environment packages by executing the following commands::

    $ virtualenv ve
    $ . ve/bin/activate
    $ pip install -r requirements.txt

Initialize the database using::

    $ ./manage.py syncdb --noinput --migrate

Then run the server usinng::

    $ ./manage.py runserver


Notes
=====

This app uses Haystack for search. When deploying remember to add a cronjob periodically updating the search index, i.e::

    0 0 * * * cd /var/praekelt/actionforwomen && . ve/bin/activate && ./manage.py update_index && deactivate
