=========
``users``
=========

The ``users`` command allows you to view user resources.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: users
   :nosubcommands:


``users list``
==============

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: users list

Example
-------

.. code-block:: console

   sh$ croud users list
   +-------------------------------+---------------------------------------------------+-------------------------------------------------------+--------------------------------------+----------+
   | email                         | organization_roles                                | project_roles                                         | uid                                  | username |
   |-------------------------------+---------------------------------------------------+-------------------------------------------------------+--------------------------------------+----------|
   | john.doe@example.com          | f167c730-1d3e-477d-a4d9-d0cb6fc51002: org_admin,  | 1e522925-caf3-4d14-9b1b-4d2e9535eb62: project_member  | 1b1e572c-5880-4e40-befd-aaaed87e74ee | john.doe |
   |                               | 5364bbac-d3ed-4f45-8579-c7f7779ca343: org_admin   |                                                       | 1b1e572c-5880-4e40-befd-aaaed87e74ee |          |
   | jane.doe@example.net          | f167c730-1d3e-477d-a4d9-d0cb6fc51002: org_member, | 1e522925-caf3-4d14-9b1b-4d2e9535eb62: project_admin,  | af84d62a-633f-4a7d-bab5-2cdcf5f6c6b6 | jane.doe |
   |                               | 5364bbac-d3ed-4f45-8579-c7f7779ca343: org_admin   | 7322af2c-bdef-4be3-be8d-857fcb61c16f: project_member, | af84d62a-633f-4a7d-bab5-2cdcf5f6c6b6 |          |
   |                               |                                                   | 9cfd05b3-65df-4cb8-bf90-1c192fa8904c: project_member  | af84d62a-633f-4a7d-bab5-2cdcf5f6c6b6 |          |
   +-------------------------------+---------------------------------------------------+-------------------------------------------------------+--------------------------------------+----------+


``users roles``
===============

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: users roles
   :nosubcommands:

.. tip::

   See :ref:`roles` for more information about the different roles.

Example
-------

.. code-block:: console

   sh$ croud users roles list
   +----------------+---------------------+
   | id             | name                |
   |----------------+---------------------|
   | org_admin      | Organization Admin  |
   | org_member     | Organization Member |
   | project_admin  | Project Admin       |
   | project_member | Project Member      |
   +----------------+---------------------+


``users roles add``
-------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: users roles add

Example
.......

.. code-block:: console

   sh$ croud users roles add \
       --user 6ac0f500-f9f8-4c12-82e2-3ad6192525d4 \
       --resource 035f1161-402e-44b4-9073-0749586091e0 \
       --role project_admin
   +--------------------------------------+--------------------------------------+---------------+
   | userId                               | resourceId                           | roleFqn       |
   |--------------------------------------+--------------------------------------+---------------|
   | 6ac0f500-f9f8-4c12-82e2-3ad6192525d4 | 035f1161-402e-44b4-9073-0749586091e0 | project_admin |
   +--------------------------------------+--------------------------------------+---------------+


``users roles remove``
----------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: users roles remove

Example
.......

.. code-block:: console

   sh$ croud users roles remove \
       --user 6ac0f500-f9f8-4c12-82e2-3ad6192525d4 \
       --resource 035f1161-402e-44b4-9073-0749586091e0 \
       --role project_admin
   +--------------------------------------+--------------------------------------+---------------+
   | userId                               | resourceId                           | roleFqn       |
   |--------------------------------------+--------------------------------------+---------------|
   | 6ac0f500-f9f8-4c12-82e2-3ad6192525d4 | 035f1161-402e-44b4-9073-0749586091e0 | project_admin |
   +--------------------------------------+--------------------------------------+---------------+


``users roles list``
--------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: users roles list

Example
.......

.. code-block:: console

   sh$ croud users roles list
   +----------------+---------------------+
   | fqn            | friendlyName        |
   |----------------+---------------------|
   | org_admin      | Organization Admin  |
   | org_member     | Organization Member |
   | project_admin  | Project Admin       |
   | project_member | Project Member      |
   +----------------+---------------------+
