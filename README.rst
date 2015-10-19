================
Action for Women
================

Getting Started
===============

Prerequisites
-------------

Make sure the following is already running on your server:

- Postgresql

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
    Then navigate to htt://localhost:8000/admin/ once the server is up and running


Notes
=====

This app uses Haystack for search. You'll need to update the search index manually::

    $ ./manage.py update_index

Running tests
=============

We use `py.test` for running our tests::

    $ py.test
