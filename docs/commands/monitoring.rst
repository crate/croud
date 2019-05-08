==============
``monitoring``
==============

The ``monitoring`` command allows you to manage monitoring tools.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: monitoring
   :nosubcommands:


``monitoring grafana``
======================
.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: monitoring grafana
   :nosubcommands:


``monitoring grafana enable``
-----------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: monitoring grafana enable

Example
.......

.. code-block:: console

   sh$ croud monioring grafana enable --project-id 57d3434e-2abc-4d6a-8542-8b33e0881599
   +----------------------------------+
   | password                         |
   |----------------------------------|
   | rX7qd2e0KmAIew74gs6AXQitnl8zbQ3W |
   +----------------------------------+

.. note::

   This command is only available for superusers.


``monitoring grafana disable``
------------------------------

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: monitoring grafana disable

Example
.......

.. code-block:: console

   sh$ croud monioring grafana disable --project-id 57d3434e-2abc-4d6a-8542-8b33e0881599
   ==> Info: Success


.. note::

   This command is only available for superusers.
