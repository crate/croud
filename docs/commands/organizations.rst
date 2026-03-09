.. _organizations:

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
   :nodescription:

.. note::

   The ``organizations auditlogs`` and ``organizations users`` subcommands
   are only available to organization admins and superusers.


``organizations create``
========================

.. note::

   The user that creates the organization will be assigned the ``org_admin``
   role for the organization.

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
   :nodescription:


``organizations auditlogs list``
--------------------------------

.. note::

   This command is only available for organization admins and superusers.

   The full context for each auditlog event is available through the JSON
   output format: ``--output-fmt json``.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations auditlogs list

Example
~~~~~~~

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

``organizations users``
=======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users
   :nosubcommands:
   :nodescription:

``organizations users add``
---------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users add

Example
~~~~~~~

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

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users list

Example
~~~~~~~

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

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations users remove

Example
~~~~~~~

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
   :nodescription:


``organizations files list``
----------------------------

.. note::

   This command is only available for organization admins and superusers.

Lists all files uploaded to an organization. The files can then be used as
data sources for data import with the ``croud clusters import-jobs create from-file`` command.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files list
   :nodescription:

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations files list \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209
   +--------------------------------------+---------------------+----------+
   | id                                   | name                | status   |
   |--------------------------------------+---------------------+----------|
   | 9b5d438f-036c-410f-b6f4-9adfb1feb252 | nyc_taxi            | UPLOADED |
   +--------------------------------------+---------------------+----------+

``organizations files create``
------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files create


``organizations files delete``
------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files delete

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations files delete \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --file-id 327ad0e6-607f-4f99-a4cc-c1e98bf28e4d
   ==> Success: File upload deleted.


``organizations files get``
------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations files get

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations files get \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --file-id 327ad0e6-607f-4f99-a4cc-c1e98bf28e4d
   +--------------------------------------+----------+----------+-------------+-------------------------------------------------------------+
   | id                                   | name     | status   | file_size   | download_url                                                |
   |--------------------------------------+----------+----------+-------------+-------------------------------------------------------------|
   | 327ad0e6-607f-4f99-a4cc-c1e98bf28e4d | nyc_taxi | UPLOADED | 107.56 MiB  | https://cratedb-file-uploads.s3.amazonaws.com/some/download |
   +--------------------------------------+----------+----------+-------------+-------------------------------------------------------------+

``organizations secrets``
=========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations secrets
   :nosubcommands:
   :nodescription:


``organizations secrets list``
------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations secrets list

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations secrets list \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209
   +--------------------------------------+--------+----------+------------------+
   | id                                   | type   | name     | description      |
   |--------------------------------------+--------+----------+------------------|
   | e9068b31-14f5-4629-b585-70b3b8ae73bf | AWS    | mysecret | **********esskey |
   +--------------------------------------+--------+----------+------------------+


``organizations secrets delete``
--------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations secrets delete

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations secrets delete \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --secret-id e9068b31-14f5-4629-b585-70b3b8ae73bf
   ==> Success: Secret deleted.


``organizations secrets create``
--------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations secrets create

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations secrests create \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --name mysecret \
       --type AWS \
       --access-key AKIAUVOXAVYAPIBHQK7I \
       --secret-key mysecretkey
   +--------------------------------------+--------+----------+------------------+
   | id                                   | type   | name     | description      |
   |--------------------------------------+--------+----------+------------------|
   | 71e7c5da-51fa-44f2-b178-d95052cbe620 | AWS    | mysecret | **********BHQK7I |
   +--------------------------------------+--------+----------+------------------+
   ==> Success: Secret created.


``organizations credits``
=========================

Credits represent a pre-paid amount of money that can be used to pay for CrateDB Cloud
resources. They can be created by superusers and applied to any organization, and are
typically used for promotional credits or free trials.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations credits
   :nosubcommands:
   :nodescription:

``organizations credits list``
------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations credits list

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations credits list \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209
   +--------------------------------------+-----------------+------------------+---------------------+------------+----------+
   | id                                   | original_amount | remaining_amount | expiration_date     | comment    | status   |
   |--------------------------------------+-----------------+------------------+---------------------+------------+----------|
   | f8207787-8458-4cab-94c1-4ca84a702154 | $300.0          | $300.0           | 2023-12-24T12:34:56 | Free Trial | ACTIVE   |
   +--------------------------------------+-----------------+------------------+---------------------+------------+----------+

``organizations credits create``
--------------------------------

.. note::

   This command is only available for superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations credits create

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations credits create \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --amount 300 \
       --expiration-date 2023-12-24T12:34:56Z \
       --comment "Free Trial" \
       --sudo
   +--------------------------------------+-----------------+---------------------+------------+----------+
   | id                                   | original_amount | expiration_date     | comment    | status   |
   |--------------------------------------+-----------------+---------------------+------------+----------|
   | f8207787-8458-4cab-94c1-4ca84a702154 | $300.0          | 2023-12-24T12:34:56 | Free Trial | ACTIVE   |
   +--------------------------------------+-----------------+---------------------+------------+----------+
   ==> Success: Credit created.

``organizations credits edit``
------------------------------

.. note::

   This command is only available for superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations credits edit

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations credits edit \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --credit-id f8207787-8458-4cab-94c1-4ca84a702154
       --amount 500
       --sudo
   +--------------------------------------+-----------------+---------------------+------------+----------+
   | id                                   | original_amount | expiration_date     | comment    | status   |
   |--------------------------------------+-----------------+---------------------+------------+----------|
   | f8207787-8458-4cab-94c1-4ca84a702154 | $500.0          | 2023-12-24T12:34:56 | Free Trial | ACTIVE   |
   +--------------------------------------+-----------------+---------------------+------------+----------+
   ==> Success: Credit edited.

``organizations credits expire``
--------------------------------

.. note::

   This command is only available for superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations credits expire

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations credits expire \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --credit-id f8207787-8458-4cab-94c1-4ca84a702154
       --sudo
   ==> Success: Credit expired.

``organizations customer``
==========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations customer
   :nosubcommands:
   :nodescription:

``organizations customer get``
------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations customer get

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations customer get \
       --org-id 89dfe980-ea1c-4108-9fa1-2161d2ac6785
   +---------+--------------+---------------+----------------------------------------------------------------------------------------------+----------------------+
   | name    |        phone | email         | address                                                                                      | tax                  |
   |---------+--------------+---------------+----------------------------------------------------------------------------------------------+----------------------|
   | Company | +33123456789 | test@crate.io | {"city": "Vienna", "country": "AT", "line1": "street", "line2": null, "postal_code": "1010"} | ATU12345678 (eu_vat) |
   +---------+--------------+---------------+----------------------------------------------------------------------------------------------+----------------------+


``organizations customer edit``
-------------------------------

.. note::

   This command is only available for organization admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: organizations customer edit

Example
~~~~~~~

.. code-block:: console

   sh$ croud organizations customer edit \
       --org-id 89dfe980-ea1c-4108-9fa1-2161d2ac6785 \
       --name Company \
       --email test@crate.io \
       --phone +33123456789 \
       --country FR \
       --city Paris \
       --line1 street \
       --line2 street \
       --postal-code 75000 \
       --tax-id FRAB123456789 \
       --tax-id-type eu_vat
   +---------+--------------+---------------+--------------------------------------------------------------------------------------------------+------------------------+
   | name    |        phone | email         | address                                                                                          | tax                    |
   |---------+--------------+---------------+--------------------------------------------------------------------------------------------------+------------------------|
   | Company | +33123456789 | test@crate.io | {"city": "Paris", "country": "FR", "line1": "street", "line2": "street", "postal_code": "75000"} | FRAB123456789 (eu_vat) |
   +---------+--------------+---------------+--------------------------------------------------------------------------------------------------+------------------------+
   ==> Success: Organization's customer info edited.
