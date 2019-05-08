============
``projects``
============

The ``projects`` command allows you to create, modify and view
projects.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects
   :nosubcommands:

``projects create``
===================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects create

Example
-------

.. code-block:: console

   sh$ croud projects create --name my-project --org-id a0df2925-cc73-4365-8a10-7ef847632b81
   +--------------------------------------+
   | id                                   |
   |--------------------------------------|
   | 035f1161-402e-44b4-9073-0749586091e0 |
   +--------------------------------------+


``projects list``
=================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects list

Example
-------

.. code-block:: console

   sh$ croud projects list
   +--------------------------------------+------------+--------------+--------------------------------------+
   | id                                   | name       | region       | organizationId                       |
   |--------------------------------------+------------+--------------+--------------------------------------|
   | 035f1161-402e-44b4-9073-0749586091e0 | my-project | eastus.azure | a0df2925-cc73-4365-8a10-7ef847632b81 |
   +--------------------------------------+------------+--------------+--------------------------------------+


``projects users``
==================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects users
   :nosubcommands:


``projects users add``
----------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects users add

Example
-------

.. code-block:: console

   sh$ croud projects users add \
       --project-id 035f1161-402e-44b4-9073-0749586091e0 \
       --user 6ac0f500-f9f8-4c12-82e2-3ad6192525d4
   ==> Success: Successfully added user to project.


``projects users remove``
-------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects users remove

Example
-------

.. code-block:: console

   sh$ croud projects users remove \
       --project-id 035f1161-402e-44b4-9073-0749586091e0 \
       --user 6ac0f500-f9f8-4c12-82e2-3ad6192525d4
   ==> Success: Successfully removed user from project.
