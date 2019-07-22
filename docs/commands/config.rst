==========
``config``
==========

Croud allows you to configure the following variables:

- The region via ``region``
- The environment via ``env``
- The output format via ``output-fmt``


``config get``
==============

You can get the values of configuration variables, like so:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config get

Example
-------

.. code-block:: console

   sh$ croud config get env
   +--------+
   | env    |
   |--------|
   | prod   |
   +--------+


``config set``
==============

You can set the values of configuration variables, like so:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config set

Example
-------

.. code-block:: console

   sh$ croud config set --region eastus.azure
   ==> Info: Region switched to eastus.azure

.. note::

    If you specify multiple flags, you can set several configuration variables
    at once.


Dealing with profiles
=====================

Croud allows you to have multiple profiles.

``config current-profile``
--------------------------

Use ``croud config current-profile`` to show the current one.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config current-profile

Example
^^^^^^^

.. code-block:: console

   sh$ croud config current-profile
   +-------------------+
   | current_profile   |
   |-------------------|
   | dev               |
   +-------------------+


``config use-profile``
----------------------

Use ``croud config use-profile`` to switch between them.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config use-profile

Example
^^^^^^^

.. code-block:: console

   sh$ croud config use-profile prod
   ==> Success: Default profile switched to 'prod'.


Global configuration
====================

Unless you've overridden any configuration option for a profile, croud is going
to use the global default.

``config get-global``
---------------------

Use ``get-global`` to show the current defaults.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config get-global

Example
^^^^^^^

.. code-block:: console

   sh$ croud config get-global region output-format
   +---------------+------------+
   | option        | value      |
   |---------------+------------|
   | region        | bregenz.a1 |
   | output-format | table      |
   +---------------+------------+


``config set-global``
---------------------

Use ``set-global`` to set or change the current defaults.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config get-global

Example
^^^^^^^

.. code-block:: console

   sh$ croud config set-global region=eastus.azure output-format=json
   ==> Info: Set 'region' to 'eastus.azure'
   ==> Info: Set 'output-format' to 'json'


Profile configuration
=====================

You can sepcify different settings per profile, depending on your use cases. If
a settings is not defined, croud is going to fall-back to its global default.

``config get-profile``
----------------------

Use ``get-profile`` to show the current defaults.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config get-profile

Example
^^^^^^^

.. code-block:: console

   sh$ croud config get-profile --profile prod region output-format
   +---------------+------------+
   | option        | value      |
   |---------------+------------|
   | region        | bregenz.a1 |
   | output-format | table      |
   +---------------+------------+


``config set-profile``
----------------------

Use ``set-profile`` to set or change the current defaults.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: config get-profile

Example
^^^^^^^

.. code-block:: console

   sh$ croud config set-profile --profile prod region=eastus.azure output-format=json
   ==> Info: Set 'region' to 'eastus.azure'
   ==> Info: Set 'output-format' to 'json'
