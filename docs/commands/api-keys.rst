.. _api-keys:

============
``api-keys``
============

The ``api-keys`` command allows you to view, edit and delete user API keys.
API keys allow easy programmatic access to the CrateDB Cloud API and have the same
permissions than the user they belong to.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: api-keys
   :nosubcommands:
   :nodescription:

``api-keys list``
=================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: api-keys list

Example
-------

.. code-block:: console

   sh$ croud api-keys list
   +--------------------------------------------+------------------------------------+--------------+-------------------------------+
   | user_id                                    | key                                | active       | last_used                     |
   |--------------------------------------------+------------------------------------+--------------+-------------------------------|
   | f167c730-1d3e-477d-a4d9-d0cb6fc51002       | my-first-key                       | TRUE         | 2022-12-05 09:00:03           |
   | 5364bbac-d3ed-4f45-8579-c7f7779ca343       | my-second-key                      | TRUE         | NULL                          |
   +--------------------------------------------+------------------------------------+--------------+-------------------------------+


``api-keys create``
===================

.. tip::

   Make sure to store the secret of the API key, as it will not be shown again after the creation.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: api-keys create
   :nosubcommands:

Example
-------

.. code-block:: console

   sh$ croud api-keys create
   +--------------------------------------------+------------------------------------+--------------+-------------------------------+
   | user_id                                    | key                                | active       | secret                        |
   |--------------------------------------------+------------------------------------+--------------+-------------------------------|
   | f167c730-1d3e-477d-a4d9-d0cb6fc51002       | my-first-key                       | TRUE         | the-secret-of-they-key        |
   +--------------------------------------------+------------------------------------+--------------+-------------------------------+



``api-keys delete``
===================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: api-keys delete
   :nosubcommands:

Example
-------

.. code-block:: console

   sh$ croud api-keys delete --api-key my-first-key
   ==> Success: API key deleted.


``api-keys edit``
=================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: api-keys edit
   :nosubcommands:

Example
-------

.. code-block:: console

   sh$ croud api-keys edit --api-key my-first-key --active false
   +------------------------------------|--------------+
   | key                                | active       |
   |------------------------------------+--------------|
   | my-first-key                       | FALSE        |
   +------------------------------------+--------------+
