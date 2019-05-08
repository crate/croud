==========
``config``
==========

Croud allows you to configure the the following variables:

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
