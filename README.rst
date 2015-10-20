================
Action for Women
================

Getting Started
===============

Prerequisites
-------------

Make sure the following is already running on your server:

- libtidy-dev
- libevent-dev
- python-dev

You can install them using::

    sudo apt-get install -qq libtidy-dev libevent-dev python-dev

Installation
------------

Create and install environment packages by executing the following commands::

    $ virtualenv ve
    $ . ve/bin/activate
    $ pip install -r requirements.txt

Initialize the database using::

    $ ./manage.py syncdb --noinput --migrate

Then run the server using (runs on http://localhost:8000)::

    $ ./manage.py runserver

In order to access the admin interface, you'll need to create a super user::

    $ ./manage.py createsuperuser
    Then navigate to http://localhost:8000/admin/ once the server is up and running


Deploying to Production
=======================

We use fabric to manage our deployments. Make sure your ssh keys are added to the server and use the following fabric command `fab <env>:<username> <command>` e.g::

    fab prod:miltontony deploy

This will deploy all the latest changes in develop to production.

Notes
=====

This app uses Haystack for search. You'll need to update the search index manually::

    $ ./manage.py update_index

Running tests
=============

We use `py.test` for running our tests::

    $ py.test
