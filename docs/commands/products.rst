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

    sh$ croud products list --kind "cluster" --region "eastus.azure"
    +-----------------------------------------+---------+-------------+--------+
    | description                             | kind    | name        | tier   |
    |-----------------------------------------+---------+-------------+--------|
    | A CrateDB cluster with standard storage | cluster | cratedb.az1 | xs     |
    | A CrateDB cluster with standard storage | cluster | cratedb.az1 | s      |
    | A CrateDB cluster with standard storage | cluster | cratedb.az1 | m      |
    | A CrateDB cluster with standard storage | cluster | cratedb.az1 | l      |
    +-----------------------------------------+---------+-------------+--------+
