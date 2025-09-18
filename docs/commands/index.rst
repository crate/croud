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


Region Support
==============

.. note::
    Most commands support the ``--region`` flag to specify the region from which
    resources are fetched or to which resources are deployed.


* If the ``--region`` flag is omitted, Croud defaults to the region specified in the current profile's API endpoint.

.. code-block:: console
    
    croud config profiles current


* The special region ``_any_`` allows listing resources across all regions, regardless of where they were deployed.
