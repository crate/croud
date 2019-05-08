=================
``organizations``
=================

The ``organizations`` command allows you to create, modify and view
organization resources.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations
   :nosubcommands:

.. note::

   The ``organizations users`` subcommand is only available to organization
   admins and superusers.


``organizations create``
========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations create

Example
-------

.. code-block:: console

   sh$ croud organizations --name my-org --plan-type 6
   +--------------------------------------+--------+------------+
   | id                                   | name   |   planType |
   |--------------------------------------+--------+------------|
   | f6c39580-5719-431d-a508-0cee4f9e8209 | my-org |          6 |
   +--------------------------------------+--------+------------+


``organizations list``
======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations list

Example
-------

.. code-block:: console

   sh$ croud organizations list
   +--------------------------------------+--------+------------+
   | id                                   | name   |   planType |
   |--------------------------------------+--------+------------|
   | f6c39580-5719-431d-a508-0cee4f9e8209 | my-org |          6 |
   +--------------------------------------+--------+------------+


``organizations users``
=======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users
   :nosubcommands:


``organizations users add``
---------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users add

Example
.......

.. code-block:: console

   sh$ croud organizations users add --user john.doe
   +--------------------------------------------------------------------------------------------------------------------------------------------+
   | user                                                                                                                                       |
   |--------------------------------------------------------------------------------------------------------------------------------------------|
   | {"email": "john.doe@example.com", "organizationId": "f6c39580-5719-431d-a508-0cee4f9e8209", "uid": "e4c6e51f-bd56-4d92-bdf8-9947531c3225"} |
   +--------------------------------------------------------------------------------------------------------------------------------------------+


``organizations users remove``
------------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users remove

Example
.......

.. code-block:: console

   sh$ croud organizations users remove --user john.doe
   +--------------------------------------------------------------------------------------------------------------------------------------------+
   | user                                                                                                                                       |
   |--------------------------------------------------------------------------------------------------------------------------------------------|
   | {"email": "john.doe@example.com", "organizationId": "f6c39580-5719-431d-a508-0cee4f9e8209", "uid": "e4c6e51f-bd56-4d92-bdf8-9947531c3225"} |
   +--------------------------------------------------------------------------------------------------------------------------------------------+
