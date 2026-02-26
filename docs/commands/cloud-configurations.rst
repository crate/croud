.. _cloud-configurations:

========================
``cloud-configurations``
========================

.. warning::

    The commands listed in this section are for internal use by CrateDB Cloud sysadmins
    (superusers) only. They are listed here only to clarify their function, since they
    appear in the full commands list available under ``--help``.

The ``cloud-configurations`` command allows you to list, get and set configuration
keys of CrateDB Cloud.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: cloud-configurations
   :nosubcommands:
   :nodescription:


``cloud-configurations list``
=============================

.. note::

   This command is only available for superusers.

List all configurations of CrateDB Cloud. Optionally it returns organization or
user specific values.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: cloud-configurations list
   :nodescription:

Example
-------

.. code-block:: console

   sh$ croud cloud-configurations list \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 --sudo
   +-------------------------------------------------+-------------+--------------------------------------+-----------+
   | key                                             | value       | organization_id                      | user_id   |
   |-------------------------------------------------+-------------+--------------------------------------|-----------|
   | CRATEDB_CLOUD_SETTING_ONE                       | 100         |                                      |           |
   | CRATEDB_CLOUD_SETTING_ORG_SPECIFIC              | 1024        | f6c39580-5719-431d-a508-0cee4f9e8209 |           |
   | CRATEDB_CLOUD_SETTING_THREE                     | 30          |                                      |           |
   +-------------------------------------------------+-------------+--------------------------------------+-----------+

``cloud-configurations get``
============================

.. note::

   This command is only available for superusers.

Get a single configuration value. Optionally it returns the organization or user specific value.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: cloud-configurations get
   :nodescription:

Example
-------

.. code-block:: console

   sh$ croud cloud-configurations get \
       --key CRATEDB_CLOUD_SETTING_ORG_SPECIFIC \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --sudo
   +-------------------------------------------------+-------------+--------------------------------------+-----------+
   | key                                             | value       | organization_id                      | user_id   |
   |-------------------------------------------------+-------------+--------------------------------------|-----------|
   | CRATEDB_CLOUD_SETTING_ORG_SPECIFIC              | 1024        | f6c39580-5719-431d-a508-0cee4f9e8209 |           |
   +-------------------------------------------------+-------------+--------------------------------------+-----------+

``cloud-configurations set``
============================

.. note::

   This command is only available for superusers.

Set a configuration value of CrateDB Cloud either globally or for a single organization or user only.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: cloud-configurations set
   :nosubcommands:
   :nodescription:

Example
-------

.. code-block:: console

   sh$ croud cloud-configurations set \
       --key CRATEDB_CLOUD_SETTING_ORG_SPECIFIC \
       --value 2048 \
       --org-id f6c39580-5719-431d-a508-0cee4f9e8209 \
       --sudo
   +-------------------------------------------------+-------------+--------------------------------------+-----------+
   | key                                             | value       | organization_id                      | user_id   |
   |-------------------------------------------------+-------------+--------------------------------------|-----------|
   | CRATEDB_CLOUD_SETTING_ORG_SPECIFIC              | 2048        | f6c39580-5719-431d-a508-0cee4f9e8209 |           |
   +-------------------------------------------------+-------------+--------------------------------------+-----------+
   ==> Success: Configuration updated.


