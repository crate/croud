.. _commands:

========
Commands
========

You can supply commands to the :ref:`Croud CLI <getting-started>` tool, like
so:

.. code-block:: console

    sh$ croud [COMMAND] [OPTIONS]

For example:

.. code-block:: console

    sh$ croud login

You can get the list of available commands, like so:

.. code-block:: console

    sh$ croud --help

To get help for a specific command, you can append ``--help``:

.. code-block:: console

    sh$ croud login --help

.. note::

   All commands support the ``--env`` flag, which can be used to select between
   the ``prod`` and ``dev`` environments. This is an internal feature used by
   developers of the Croud CLI tool itself.

.. rubric:: Available Commands

.. toctree::
   :maxdepth: 1

   clusters
   config
   consumers
   authentication
   me
   monitoring
   organizations
   projects
   products
   users
