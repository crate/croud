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
   | Crate.io's Offering to connect Azure's EventHub to CrateDB. | consumer | eventhub-consumer | 1 - 1 (1 - 1 instances)   | xs     |
   | Crate.io's Offering to connect Azure's EventHub to CrateDB. | consumer | eventhub-consumer | 1 - 3 (1 - 3 instances)   | s      |
   | Crate.io's Offering to connect Azure's EventHub to CrateDB. | consumer | eventhub-consumer | 1 - 6 (1 - 6 instances)   | m      |
   | Crate.io's Offering to connect Azure's EventHub to CrateDB. | consumer | eventhub-consumer | 1 - 18 (1 - 18 instances) | l      |
   +-------------------------------------------------------------+----------+-------------------+---------------------------+--------+
