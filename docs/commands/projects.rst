.. _projects:

============
``projects``
============

The ``projects`` command allows you to create, modify and view
projects.

Projects are internal resources that contains the clusters.
They are automatically created when you create a cluster, but you can also
create them manually and assign clusters to them.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects
   :nosubcommands:

``projects create``
===================

Creates a project in an organization.

.. warning::

   Some optional arguments and for Edge regions only. An Edge region allows you to
   host CrateDB instances in your own infrastructure however this feature is not
   maintained anymore. It is not recommended to use it.

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

Deletes a project.

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
=================

Edits a project.

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
   ==> Success: Project edited.

``projects list``
=================

Lists the projects you have access to.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects list

Example
-------

.. code-block:: console

   sh$ croud projects list
   +--------------------------------------+-----------------+--------------------+--------------------------------------+-------------------+
   | id                                   | name            | region             | organization_id                      | backup_location   |
   |--------------------------------------+-----------------+--------------------+--------------------------------------+-------------------|
   | 035f1161-402e-44b4-9073-0749586091e0 | my-project      | aks1.eastus.azure  | a0df2925-cc73-4365-8a10-7ef847632b81 | default           |
   +--------------------------------------+-----------------+--------------------+--------------------------------------+-------------------+


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

Adds a user to a project.

It allows the user to access the project and its clusters with the specified role.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects users add

Example
~~~~~~~

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

Lists the users that have access to a project.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects users list

Example
~~~~~~~

.. code-block:: console

   sh$ croud projects users list \
       --project-id 035f1161-402e-44b4-9073-0749586091e0
   +--------------------------------------+----------------------+----------+----------------+
   | uid                                  | email                | username | project_roles  |
   |--------------------------------------+----------------------+----------+----------------|
   | 6ac0f500-f9f8-4c12-82e2-3ad6192525d4 | john.doe@example.com | john.doe | project_admin  |
   +--------------------------------------+----------------------+----------+----------------+


``projects users remove``
-------------------------

Removes a user from a project.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: projects users remove

Example
~~~~~~~

.. code-block:: console

   sh$ croud projects users remove \
       --project-id 035f1161-402e-44b4-9073-0749586091e0 \
       --user john.doe@example.com
   ==> Success: User removed from project.
