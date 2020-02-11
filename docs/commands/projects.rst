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
   ==> Success: Project created.


``projects delete``
===================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects delete

Example
-------

.. code-block:: console

   sh$ croud projects delete --project-id 035f1161-402e-44b4-9073-0749586091e0
   Are you sure you want to delete the project? [yN] y
   ==> Success: Project deleted.

``projects edit``
======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects edit

Example
-------

.. code-block:: console

   sh$ croud projects edit --p f6c39580-5719-431d-a508-0cee4f9e8209  --name new-name
   +--------------------------------------+-------------+
   | project_id                           | name        |
   |--------------------------------------+-------------+
   | f6c39580-5719-431d-a508-0cee4f9e8209 | new-name    |
   +--------------------------------------+-------------+
   ==> Success: Project name edited.

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
       --role project_member \
       --user john.doe@example.com
   +--------------------------------------+----------------+--------------------------------------+
   | project_id                           | role_fqn       | user_id                              |
   |--------------------------------------+----------------+--------------------------------------|
   | 035f1161-402e-44b4-9073-0749586091e0 | project_member | 6ac0f500-f9f8-4c12-82e2-3ad6192525d4 |
   +--------------------------------------+----------------+--------------------------------------+
   ==> Success: User added to project.


``projects users list``
-----------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects users list

Example
.......

.. code-block:: console

   sh$ croud projects users list \
       --project-id 035f1161-402e-44b4-9073-0749586091e0
   +----------------------+----------------+----------+--------------------------------------+
   | email                | project_roles  | username | uid                                  |
   |----------------------+----------------+----------+--------------------------------------|
   | john.doe@example.com | project_member | john.doe | 6ac0f500-f9f8-4c12-82e2-3ad6192525d4 |
   +----------------------+----------------+----------+--------------------------------------+


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
       --user john.doe@example.com
   ==> Success: User removed from project.
