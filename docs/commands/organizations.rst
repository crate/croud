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

   The ``organizations auditlogs`` and ``organizations users`` subcommands
   are only available to organization admins and superusers.


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

   sh$ croud organizations create --name my-org
   +--------------------------------------+--------+------------+
   | id                                   | name   |   planType |
   |--------------------------------------+--------+------------|
   | f6c39580-5719-431d-a508-0cee4f9e8209 | my-org |          3 |
   +--------------------------------------+--------+------------+
   ==> Success: Organization created.


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
   | f6c39580-5719-431d-a508-0cee4f9e8209 | my-org |          3 |
   +--------------------------------------+--------+------------+


``organizations edit``
======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations edit

Example
-------

.. code-block:: console

   sh$ croud organizations edit --name new-name
   +--------------------------------------+-------------+-------------+
   | id                                   | name        |   plan_type |
   |--------------------------------------+-------------+-------------|
   | f6c39580-5719-431d-a508-0cee4f9e8209 | new-name    |           3 |
   +--------------------------------------+-------------+-------------+
   ==> Success: Organization edited.


``organizations delete``
========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations delete

Example
-------

.. code-block:: console

   sh$ croud organizations delete \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209
   Are you sure you want to delete the organization? [yN] y
   ==> Success: Organization deleted.


``organizations auditlogs``
===========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations auditlogs
   :nosubcommands:


``organizations auditlogs list``
--------------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations auditlogs list

Example
.......

.. code-block:: console

   sh$ croud organizations auditlogs list \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209
   +------------------------+--------------------------------------+----------------------------------+
   | action                 | actor                                | created                          |
   |------------------------+--------------------------------------+----------------------------------|
   | product.create_cluster | e4c6e51f-bd56-4d92-bdf8-9947531c3225 | 2019-11-05T12:35:23.168000+00:00 |
   | project.add_user       | e4c6e51f-bd56-4d92-bdf8-9947531c3225 | 2019-11-05T12:22:31.796000+00:00 |
   | project.create         | e4c6e51f-bd56-4d92-bdf8-9947531c3225 | 2019-11-05T12:22:31.196000+00:00 |
   | organization.add_user  | e4c6e51f-bd56-4d92-bdf8-9947531c3225 | 2019-11-05T12:20:57.610000+00:00 |
   | organization.create    | e4c6e51f-bd56-4d92-bdf8-9947531c3225 | 2019-11-05T12:20:57.598000+00:00 |
   +------------------------+--------------------------------------+----------------------------------+

.. note::

   The full context for each auditlog event is available through the JSON
   output format:

   .. code-block:: console

      sh$ croud organizations auditlogs list \
          --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
          --output-fmt json



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

   sh$ croud organizations users add \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --role org_member \
       --user john.doe@example.com
   +--------------------------------------+------------+--------------------------------------+
   | organization_id                      | role_fqn   | user_id                              |
   |--------------------------------------+------------+--------------------------------------|
   | f6c39580-5719-431d-a508-0cee4f9e8209 | org_member | e4c6e51f-bd56-4d92-bdf8-9947531c3225 |
   +--------------------------------------+------------+--------------------------------------+
   ==> Success: User added to organization.


``organizations users list``
----------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users list

Example
.......

.. code-block:: console

   sh$ croud organizations users list \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209
   +----------------------+--------------------+----------+--------------------------------------+
   | email                | organization_roles | username | uid                                  |
   |----------------------+--------------------+----------+--------------------------------------|
   | john.doe@example.com | org_admin          | john.doe | e4c6e51f-bd56-4d92-bdf8-9947531c3225 |
   +----------------------+--------------------+----------+--------------------------------------+


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

   sh$ croud organizations users remove \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --user john.doe@example.io
   ==> Success: User removed from organization.


``organizations files``
=======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files
   :nosubcommands:


``organizations files list``
----------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files list

Example
.......

.. code-block:: console

   sh$ croud organizations files list \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209
   +--------------------------------------+---------------------+----------+
   | id                                   | name                | status   |
   |--------------------------------------+---------------------+----------|
   | 9b5d438f-036c-410f-b6f4-9adfb1feb252 | nyc_taxi            | UPLOADED |
   +--------------------------------------+---------------------+----------+


``organizations files delete``
------------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files delete

Example
.......

.. code-block:: console

   sh$ croud organizations files delete \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --file-id 327ad0e6-607f-4f99-a4cc-c1e98bf28e4d
   ==> Success: File upload deleted.


``organizations files get``
------------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files get

Example
.......

.. code-block:: console

   sh$ croud organizations files get \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --file-id 327ad0e6-607f-4f99-a4cc-c1e98bf28e4d
   +--------------------------------------+----------+----------+-------------+-------------------------------------------------------------+
   | id                                   | name     | status   | file_size   | download_url                                                |
   |--------------------------------------+----------+----------+-------------+-------------------------------------------------------------|
   | 327ad0e6-607f-4f99-a4cc-c1e98bf28e4d | nyc_taxi | UPLOADED | 107.56 MiB  | https://cratedb-file-uploads.s3.amazonaws.com/some/download |
   +--------------------------------------+----------+----------+-------------+-------------------------------------------------------------+

