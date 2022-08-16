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

   Most commands support the ``--region`` flag to specify the region from which
   resources are fetched or to which resources are deployed. If the
   ``--region`` argument is omitted, the region falls back to the region of the
   API endpoint as specified in the current profile (see the
   :ref:`documentation for the command <cmd-config-profiles-current>` ``croud
   config profiles current``).  The ``_any_`` region is special, in that it
   permits listing resources regardless of where they're deployed in CrateDB
   Cloud.

.. rubric:: Available commands

.. toctree::
   :maxdepth: 1

   clusters
   config
   authentication
   me
   organizations
   projects
   products
   subscriptions
   users
   regions
