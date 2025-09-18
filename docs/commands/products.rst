.. _products:

============
``products``
============

The ``products`` command allows you to view the available products.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: products
   :nosubcommands:


``products list``
=================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: products list

Example
-------

.. code-block:: console

   sh$ croud products list --region "eastus.azure"
   +-------------------------------------------------------------+----------+-------------------+---------------------------+--------+
   | description                                                 | kind     | name              | scale_summary             | tier   |
   |-------------------------------------------------------------+----------+-------------------+---------------------------+--------|
   | A CrateDB cluster with standard storage                     | cluster  | cratedb.az1       | 0 - 1 (1 - 3 nodes)       | xs     |
   | A CrateDB cluster with standard storage                     | cluster  | cratedb.az1       | 0 - 1 (3 - 5 nodes)       | s      |
   | A CrateDB cluster with standard storage                     | cluster  | cratedb.az1       | 0 - 2 (3 - 7 nodes)       | m      |
   | A CrateDB cluster with standard storage                     | cluster  | cratedb.az1       | 0 - 3 (3 - 9 nodes)       | l      |
   +-------------------------------------------------------------+----------+-------------------+---------------------------+--------+
