.. _getting-started:

===============
Getting Started
===============

Installation
============

Croud CLI is available as a `pip`_ package.

To install, run:

.. code-block:: console

    sh$ pip install croud

To update, run:

.. code-block:: console

   sh$ pip install -U croud

Run
===

Verify your installation, like so:

.. code-block:: console

    sh$ croud --version

When using Croud, you must supply a *command*.

For example:

.. code-block:: console

    sh$ croud login

Here, ``login`` is supplied as a command. The will open a browser window for
you to authenticate with `CrateDB Cloud`_. You will need to do this before
issuing any further commands.

Alternatively, use the ``CRATEDB_CLOUD_API_KEY`` and ``CRATEDB_CLOUD_API_SECRET``
environment variables for headless authentication without a configuration file.

From here, you can go on to use :ref:`commands <commands>` to manage your
configuration values, projects, clusters, organizations, and users.

Command-line options
====================

Croud supports the following command-line options:

+------------------------+--------------------------------------------------+
| Argument               | Description                                      |
+------------------------+--------------------------------------------------+
| ``-h``,                | Print the help message, then exits.              |
| ``--help``             |                                                  |
+------------------------+--------------------------------------------------+
| ``-v``,                | Prints the program's version number, then exits. |
| ``--version``          |                                                  |
+------------------------+--------------------------------------------------+

.. TIP::

    Some Croud :ref:`commands <commands>` take additional options.

Shell auto-complete
===================

Croud supports shell auto-completions for ``bash``, ``zsh`` and ``tcsh``:

.. code-block:: console

    sh$ croud --print-completion {bash,zsh,tcsh}

Refer to the documentation of your specific shell for installation instructions.

.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
.. _pip: https://pypi.org/project/pip/
