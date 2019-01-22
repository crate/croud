.. _getting-started:

===============
Getting Started
===============

.. rubric:: Table of Contents

.. contents::
   :local:

Installation
============

The Croud CLI is available as a `pip`_ package.

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

From here, you can go on to use :ref:`commands <commands>` to manage your
configuration values, projects, clusters, organizations, and users.

Command-Line Options
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

.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
.. _pip: https://pypi.python.org/pypi/pip
