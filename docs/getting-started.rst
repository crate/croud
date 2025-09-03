.. _getting-started:

===============
Getting Started
===============

Installation
============

The Croud CLI is available as a Python package on `PyPI`_.

To install it, run:

.. code-block:: console

    sh$ pip install croud

To update to the latest version, run:

.. code-block:: console

   sh$ pip install -U croud

Running Croud
=============

After installation, verify it by checking the version:

.. code-block:: console

    sh$ croud --version

You must authenticate before using most commands. To log in:

.. code-block:: console

    sh$ croud login

This will open a browser window to authenticate with your CrateDB Cloud account.

.. TIP::

    For headless environments (e.g., CI/CD pipelines), you can authenticate by setting the following environment variables instead of running ``croud login``:
    
    * ``CRATEDB_CLOUD_API_KEY``

    * ``CRATEDB_CLOUD_API_SECRET``

Once logged in, you can begin using Croud to manage your projects, clusters, organizations, users, and more.

Command-line Options
====================

Croud supports the following command-line options:

+------------------------+--------------------------------------------------+
| Argument               | Description                                      |
+------------------------+--------------------------------------------------+
| ``-h``                 |                                                  |
|                        | Show the help message, then exits                |
| ``--help``             |                                                  |
+------------------------+--------------------------------------------------+
| ``-v``                 |                                                  |
|                        | Display the current version, then exits          |
| ``--version``          |                                                  |
+------------------------+--------------------------------------------------+

Some Croud :ref:`commands <commands>` support additional subcommands and flags. Use --help after any command for more information:

.. code-block:: console

    sh$ croud clusters --help

Shell Auto-Completion
=====================
Croud offers tab-completion support for the following shells:

* ``bash``

* ``zsh``

* ``tcsh``

To print the appropriate completion script, run:

.. code-block:: console

    sh$ croud --print-completion {bash,zsh,tcsh}

Refer to your shell’s documentation for instructions on how to install the completion script.

.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
.. _PyPI: https://pypi.org/project/croud/
