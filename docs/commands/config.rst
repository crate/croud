==========
``config``
==========

The command ``croud config`` offers multiple subcommands to manage its
configuration.


``config show``
===============

You can show your full configuration, like so:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config show

Example
-------

.. code-block:: console

   sh$ croud config show
   ==> Info: Configuration file /home/me/.config/Crate/croud.yaml
   default-format: table
   current-profile: bregenz.a1
   profiles:
     bregenz.a1:
       auth-token: xxxxxxxxxx
       endpoint: https://bregenz.a1.cratedb.cloud
       format: table
     eastus2.azure:
       auth-token: xxxxxxxxxx
       endpoint: https://eastus2.azure.cratedb.cloud
       format: table
     westeurope.azure:
       auth-token: xxxxxxxxxx
       endpoint: https://westeurope.azure.cratedb.cloud
       format: table

Note, that the values of ``auth-token`` are masked.


``config profiles current``
===========================

You can list your current profile, like so:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config profiles current

Example
-------

.. code-block:: console

   sh$ croud config profiles current
   +------------+----------------------------------+----------+
   | name       | endpoint                         | format   |
   |------------+----------------------------------+----------|
   | bregenz.a1 | https://bregenz.a1.cratedb.cloud | table    |
   +------------+----------------------------------+----------+


``config profiles use``
=======================

You can switch to a different profile, like so:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config profiles use


Example
-------

.. code-block:: console

   sh$ croud config profiles use eastus2.azure
   ==> Info: Switched to profile 'eastus2.azure'.
