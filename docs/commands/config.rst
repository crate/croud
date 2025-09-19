.. _config:

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
   current-profile: cratedb.cloud
   profiles:
     cratedb.cloud:
       auth-token: xxxxxxxxxx
       endpoint: https://console.cratedb.cloud
       format: table
       region: _any_

Note, that the values of ``auth-token`` are masked.

.. _cmd-config-profiles-current:

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
   +---------------+----------------------------------+----------+
   | name          | endpoint                         | format   |
   |---------------+----------------------------------+----------|
   | cratedb.cloud | https://console.cratedb.cloud    | table    |
   +---------------+----------------------------------+----------+


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

   sh$ croud config profiles use some.other
   ==> Info: Switched to profile 'some.other'.
