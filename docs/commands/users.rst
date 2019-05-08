=========
``users``
=========

The ``users`` command allows you to create, modify and view user resources.

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
   +--------------------------------------+-------------------------------+-------------------+
   | uid                                  | email                         | username          |
   |--------------------------------------+-------------------------------+-------------------|
   | e4c6e51f-bd56-4d92-bdf8-9947531c3225 | john.doe@example.com          | Google_1234567890 |
   +--------------------------------------+-------------------------------+-------------------+


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
