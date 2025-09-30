.. _commands:

========
Commands
========

Croud follows the standard CLI syntax:

.. code-block:: console

    sh$ croud [COMMAND] [OPTIONS]

Example: Login
==============

.. code-block:: console

    sh$ croud login

This command opens a browser window so you can authenticate with CrateDB Cloud.
You must log in before using other commands (unless you're using headless authentication).

List Available Commands
=======================

To see a list of all available commands, use:

.. code-block:: console

    sh$ croud --help

To view help and usage details for a specific command, append ``--help`` to it:

.. code-block:: console

    sh$ croud login --help

Available commands
==================

.. toctree::
   :maxdepth: 1
   :hidden:

   clusters
   data-import-export
   config
   authentication
   me
   organizations
   projects
   products
   subscriptions
   users
   api-keys
   regions
   scheduled-jobs
   cloud-configurations

* :ref:`clusters` -- Manage CrateDB Cloud clusters

* :ref:`data-import-export` -- Import and export data jobs

* :ref:`config`  -- Manage local Croud configuration

* :ref:`authentication` -- Authenticate with CrateDB Cloud

* :ref:`me` -- View current user information

* :ref:`organizations` -- Manage organizations

* :ref:`projects` -- Manage projects

* :ref:`products` -- View available CrateDB products

* :ref:`subscriptions` -- View and manage active subscriptions

* :ref:`users` -- Manage users

* :ref:`api-keys` -- Create and manage API keys

* :ref:`regions` -- List available deployment regions

* :ref:`scheduled-jobs` -- View and manage scheduled jobs

* :ref:`cloud-configurations` -- Manage predefined deployment configurations


Region Support
==============

.. note::
    Most commands support the ``--region`` flag to specify the region from which
    resources are fetched or to which resources are deployed.


* If the ``--region`` flag is omitted, Croud defaults to the region specified in the current profile's API endpoint.

.. code-block:: console
    
    sh$ croud config profiles current

* The special region ``_any_`` allows listing resources across all regions, regardless of where they were deployed.
